import time
import datetime
import sys
import traceback
from django.http import JsonResponse
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

# API 视图：查询所有账户的资产及持仓数据
def get_account_info(request):
    try:
        # 创建交易接口实例
        path = r'D:\01_Software\迅投极速交易终端 睿智融科版\userdata'
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
        accounts = xt_trader.query_account_infos()
        account_list = []
        for acc in accounts:
            # 订阅该账户的交易回调
            subscribe_result = xt_trader.subscribe(acc)
            # 查询账户资产信息
            asset = xt_trader.query_stock_asset(acc)
            if asset is None:
                continue
            # 查询该账户的持仓信息
            positions = xt_trader.query_stock_positions(acc)
            pos_list = []
            if positions:
                for pos in positions:
                    pos_list.append({
                        'account_type': pos.account_type,#账号类型
                        'account_id': pos.account_id,#账号
                        'stock_code': pos.stock_code,#证券代码
                        'volume': pos.volume,#持仓数量
                        'can_use_volume': pos.can_use_volume,#可用数量
                        'open_price': pos.open_price,#开仓价
                        'market_value': pos.market_value,#市值
                    })
            account_list.append({
                'account_type': asset.account_type,#账号类型
                'account_id': asset.account_id,#账号
                'cash': asset.cash,#可用金额
                'frozen_cash': asset.frozen_cash,#冻结金额
                'market_value': asset.market_value,#
                'total_asset': asset.total_asset,#持仓市值
                'positions': pos_list,
            })

        return JsonResponse({'accounts': account_list})
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)
