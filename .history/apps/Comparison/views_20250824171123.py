import time
import datetime
import sys
import traceback
from django.http import JsonResponse
from rest_framework.decorators import api_view
from django.conf import settings
from xtquant import xtdata
from xtquant.xttrader import XtQuantTrader, XtQuantTraderCallback
from xtquant.xttype import StockAccount


# 定义交易回调类
class MyXtQuantTraderCallback(XtQuantTraderCallback):
    def on_disconnected(self):
        print(datetime.datetime.now(), '连接断开回调')

    def on_stock_order(self, order):
        print(datetime.datetime.now(), '委托回调 投资备注', order.order_remark)

    def on_stock_trade(self, trade):
        print(datetime.datetime.now(), '成交回调', trade.order_remark,
              f"委托方向(48买 49卖) {trade.offset_flag} 成交价格 {trade.traded_price} 成交数量 {trade.traded_volume}")

    def on_order_error(self, order_error):
        print(f"委托报错回调 {order_error.order_remark} {order_error.error_msg}")

    def on_cancel_error(self, cancel_error):
        print(datetime.datetime.now(), sys._getframe().f_code.co_name)

    def on_order_stock_async_response(self, response):
        print(f"异步委托回调 投资备注: {response.order_remark}")

    def on_cancel_order_stock_async_response(self, response):
        print(datetime.datetime.now(), sys._getframe().f_code.co_name)

    def on_account_status(self, status):
        print(datetime.datetime.now(), sys._getframe().f_code.co_name)


@api_view(['GET'])
def asset_comparison(request):
    try:
        # 从请求参数中获取账户 ID
        account_id = request.GET.get('account_id')
        if not account_id:
            return JsonResponse({'error': '未提供账户 ID'}, status=400)
        # 创建交易接口实例
        path = settings.XT_CONFIG['USERDATA_PATH']  # 使用统一配置
        session_id = int(time.time())
        xt_trader = XtQuantTrader(path, session_id)
        callback = MyXtQuantTraderCallback()
        xt_trader.register_callback(callback)
        xt_trader.start()

        # 建立交易连接，返回 0 表示连接成功
        connect_result = xt_trader.connect()
        if connect_result != 0:
            return JsonResponse({
                'error': '连接交易接口失败',
                'connect_result': connect_result
            }, status=500)

        # 查询所有账户信息
        acc = StockAccount(account_id)

        # 订阅该账户的交易回调
        subscribe_result = xt_trader.subscribe(acc)
        if subscribe_result != 0:
            return JsonResponse({
                'error': '订阅账户失败',
                'subscribe_result': subscribe_result
            }, status=500)

        # 查询账户资产信息
        asset = xt_trader.query_stock_asset(acc)
        if not asset:
            return JsonResponse({'error': '未查询到账户资产信息'}, status=500)

        # 查询该账户的持仓信息
        positions = xt_trader.query_stock_positions(acc)
        if not positions:
            return JsonResponse({'error': '未查询到持仓信息'}, status=500)

        # 提取并计算用户持仓信息
        pos_list = []
        total_market_value = asset.market_value  # 总持仓市值
        for pos in positions:
            stock_code = pos.stock_code  # 股票代码
            market_value = pos.market_value  # 市值
            avg_price = pos.avg_price  # 成本价
            latest_price = pos.open_price  # 最新价（假设pos对象有此属性）

            # 计算各支股票的资产占比
            asset_ratio = market_value / total_market_value if total_market_value > 0 else 0

            # 计算当日涨幅（收益率）
            daily_return = ((latest_price - avg_price) / avg_price) * 100 if avg_price > 0 else 0

            pos_list.append({

                'stock_code': stock_code,  # x轴数据：股票代码
                'asset_ratio': round(asset_ratio, 4),  # y轴数据1：资产占比
                'market_value': round(market_value, 2),  # y轴数据2：股票市值
                'daily_return': round(daily_return, 2)  # y轴数据3：当日涨幅（百分比形式）
            })

        # 返回结果
        return JsonResponse({
            'total_market_value': round(total_market_value, 2),
            'positions': pos_list
        })

    except Exception as e:
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)