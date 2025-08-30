import time
import datetime
import sys
import traceback
from django.http import JsonResponse
from rest_framework.decorators import api_view
from xtquant import xtdata
from xtquant.xttrader import XtQuantTrader, XtQuantTraderCallback
from xtquant.xttype import StockAccount
from django.conf import settings

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
# API 视图：查询所有账户的资产及持仓数据
def get_account_info(request):
    try:
        # 从配置文件中获取迅投路径
        path = settings.XT_CONFIG['USERDATA_PATH']  # 从 setting 文件获取迅投路径
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
                        'frozen_volume':pos.frozen_volume,#冻结数量
                        'on_road_volume':pos.on_road_volume,#在途股份
                        'yesterday_volume':pos.yesterday_volume,#昨夜拥股
                        'avg_price':pos.avg_price,#成本价
                    })
            account_list.append({
                'account_type': asset.account_type,#账号类型
                'account_id': asset.account_id,#账号
                'cash': asset.cash,#可用金额
                'frozen_cash': asset.frozen_cash,#冻结金额
                'market_value': asset.market_value,#持仓市值
                'total_asset': asset.total_asset,#总资产
                'positions': pos_list,
            })

        return JsonResponse({'accounts': account_list})
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)


@api_view(['GET'])
def get_asset_category(request):
    """获取资产类别分布数据"""
    try:
        account_id = request.GET.get('account_id', '40000326')
        
        # 这里应该基于真实持仓数据计算行业分布
        # 实际实现时需要：
        # 1. 查询账户持仓
        # 2. 根据股票代码判断行业分类
        # 3. 计算各行业资产占比
        
        # 暂时返回模拟数据
        category_data = [
            {
                "name": "银行股",
                "value": 216000,
                "percentage": 7.6
            },
            {
                "name": "白酒股", 
                "value": 228000,
                "percentage": 8.0
            },
            {
                "name": "科技股",
                "value": 342000,
                "percentage": 12.0
            },
            {
                "name": "医药股",
                "value": 285000,
                "percentage": 10.0
            },
            {
                "name": "新能源",
                "value": 513000,
                "percentage": 18.0
            },
            {
                "name": "消费股",
                "value": 399000,
                "percentage": 14.0
            },
            {
                "name": "房地产",
                "value": 171000,
                "percentage": 6.0
            },
            {
                "name": "金融服务",
                "value": 228000,
                "percentage": 8.0
            }
        ]
        
        return JsonResponse({
            'categoryData': category_data,
            'is_mock': True,  # 标记为模拟数据
            'message': '此数据基于模拟计算，实际实现需要基于持仓数据计算行业分布'
        })
        
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)
