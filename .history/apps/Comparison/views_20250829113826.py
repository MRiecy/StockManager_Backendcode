import time
import datetime
import sys
import traceback
from django.http import JsonResponse
from rest_framework.decorators import api_view
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
        path = r'E:\迅投极速交易终端 睿智融科版\userdata'
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


@ 10,
                "growthRate": round((12.3 - i * 0.5) * 10) / 10
            })
        
        weekly_data.reverse()  # 按时间顺序排序
        
        return JsonResponse({
            'weekly_data': weekly_data,
            'current_total_assets': 4100000,
            'current_market_value': 2850000,
            'current_return_rate': 8.0,
            'is_mock': True,  # 标记为模拟数据
            'message': '此数据基于模拟计算，实际实现需要XtQuant历史数据支持'
        })
        
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)


@api_view(['GET'])
def area_comparison(request):
    """地区对比数据API"""
    try:
        account_id = request.GET.get('account_id', '40000326')
        
        # 基于股票代码判断地区分布
        # 实际实现时需要：
        # 1. 查询账户持仓
        # 2. 根据股票代码判断地区
        # 3. 计算各地区资产分布
        
        area_data = [
            {
                "region": "上海",
                "totalAssets": 820000,api_view(['GET'])
def yearly_comparison(request):
    """年度对比数据API"""
    try:
        account_id = request.GET.get('account_id', '40000326')
        
        # 这里应该从XtQuant获取历史数据，暂时返回模拟数据
        # 实际实现时需要：
        # 1. 连接XtQuant历史数据中心
        # 2. 查询账户历史资产数据
        # 3. 计算年度对比数据
        
        yearly_data = [
            {
                "timePeriod": "2022",
                "totalAssets": 3500000,
                "marketValue": 2400000,
                "returnRate": 5.2,
                "growthRate": 8.5
            },
            {
                "timePeriod": "2023", 
                "totalAssets": 3800000,
                "marketValue": 2600000,
                "returnRate": 7.8,
                "growthRate": 12.3
            },
            {
                "timePeriod": "2024",
                "totalAssets": 4100000,
                "marketValue": 2850000,
                "returnRate": 8.0,
                "growthRate": 15.7
            }
        ]
        
        return JsonResponse({
            'yearly_data': yearly_data,
            'current_total_assets': 4100000,
            'current_market_value': 2850000,
            'current_return_rate': 8.0,
            'is_mock': True,  # 标记为模拟数据
            'message': '此数据基于模拟计算，实际实现需要XtQuant历史数据支持'
        })
        
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)


@api_view(['GET'])
def weekly_comparison(request):
    """每周对比数据API"""
    try:
        account_id = request.GET.get('account_id', '40000326')
        
        # 生成最近6周的模拟数据
        current_date = datetime.datetime.now()
        weekly_data = []
        
        for i in range(6):
            week_date = current_date - datetime.timedelta(weeks=i)
            year = week_date.year
            week_num = week_date.isocalendar()[1]
            
            weekly_data.append({
                "timePeriod": f"{year}-W{week_num:02d}",
                "totalAssets": round(4100000 * (1 - i * 0.02)),
                "marketValue": round(2850000 * (1 - i * 0.02)),
                "returnRate": round((8.0 - i * 0.3) * 10) /
                "returnRate": "8.5%",
                "maxDrawdown": 28.8
            },
            {
                "region": "深圳", 
                "totalAssets": 712500,
                "returnRate": "7.8%",
                "maxDrawdown": 25.0
            },
            {
                "region": "北京",
                "totalAssets": 570000,
                "returnRate": "9.2%",
                "maxDrawdown": 20.0
            },
            {
                "region": "广州",
                "totalAssets": 342000,
                "returnRate": "6.5%",
                "maxDrawdown": 12.0
            },
            {
                "region": "杭州",
                "totalAssets": 228000,
                "returnRate": "7.0%",
                "maxDrawdown": 8.0
            },
            {
                "region": "成都",
                "totalAssets": 114000,
                "returnRate": "5.8%",
                "maxDrawdown": 4.0
            },
            {
                "region": "其他",
                "totalAssets": 63500,
                "returnRate": "4.2%",
                "maxDrawdown": 2.2
            }
        ]
        
        return JsonResponse({
            'area_data': area_data,
            'is_mock': True,  # 标记为模拟数据
            'message': '此数据基于模拟计算，实际实现需要基于持仓数据计算地区分布'
        })
        
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)