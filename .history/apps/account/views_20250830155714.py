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
    """获取资产类别分布数据 - 基于真实持仓数据计算行业分类"""
    try:
        account_id = request.GET.get('account_id', '40000326')
        
        # 1. 连接XtQuant交易接口获取持仓数据
        import xtquant.xttrader as xttrader
        from xtquant.xttype import StockAccount
        from django.conf import settings
        
        # 2. 创建交易接口实例
        path = settings.XT_CONFIG['USERDATA_PATH']
        session_id = int(time.time())
        xt_trader = xttrader.XtQuantTrader(path, session_id)
        callback = MyXtQuantTraderCallback()
        xt_trader.register_callback(callback)
        xt_trader.start()

        # 3. 建立交易连接
        connect_result = xt_trader.connect()
        if connect_result != 0:
            time.sleep(1)
            connect_result = xt_trader.connect()
        if connect_result != 0:
            raise Exception(f'连接交易接口失败，错误码: {connect_result}')

        # 4. 查询账户持仓
        acc = StockAccount(account_id)
        positions = xt_trader.query_stock_positions(acc)
        
        if not positions:
            # 如果没有持仓，返回空数据
            return JsonResponse({
                'categoryData': [],
                'data_available': False,
                'message': '账户无持仓，无法计算资产类别分布'
            })
        
        # 5. 基于持仓计算行业分类
        category_data = calculate_industry_distribution(positions)
        
        return JsonResponse({
            'categoryData': category_data,
            'data_available': True,
            'message': '基于真实持仓数据计算行业分布',
            'position_count': len(positions)
        })
        
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({
            'error': str(e),
            'data_available': False,
            'message': '真实数据查询失败，前端使用模拟数据'
        }, status=500)


def calculate_industry_distribution(positions):
    """基于持仓计算行业分类分布"""
    # 股票代码到行业的映射
    stock_industry_map = {
        '000001.SZ': '银行',      # 平安银行
        '000002.SZ': '房地产',    # 万科A
        '600000.SH': '银行',      # 浦发银行
        '600036.SH': '银行',      # 招商银行
        '600519.SH': '白酒',      # 贵州茅台
        '000858.SZ': '白酒',      # 五粮液
        '002415.SZ': '科技',      # 海康威视
        '600276.SH': '医药',      # 恒瑞医药
        '000858.SZ': '白酒',      # 五粮液
        '002415.SZ': '科技',      # 海康威视
        '600276.SH': '医药',      # 恒瑞医药
    }
    
    # 按行业统计资产
    industry_assets = {}
    total_market_value = 0
    
    for pos in positions:
        stock_code = pos.stock_code
        market_value = pos.market_value
        total_market_value += market_value
        
        # 获取行业分类
        industry = stock_industry_map.get(stock_code, '其他')
        
        if industry not in industry_assets:
            industry_assets[industry] = {
                'market_value': 0,
                'positions': []
            }
        
        industry_assets[industry]['market_value'] += market_value
        industry_assets[industry]['positions'].append(pos)
    
    # 转换为前端期望的格式
    category_data = []
    for industry, data in industry_assets.items():
        # 计算资产占比
        percentage = round((data['market_value'] / total_market_value) * 100, 1) if total_market_value > 0 else 0
        
        # 计算平均收益率
        total_return = 0
        valid_positions = 0
        for pos in data['positions']:
            if hasattr(pos, 'avg_price') and hasattr(pos, 'open_price'):
                avg_price = pos.avg_price
                current_price = pos.open_price
                if avg_price > 0:
                    pos_return = ((current_price - avg_price) / avg_price) * 100
                    total_return += pos_return
                    valid_positions += 1
        
        avg_return = total_return / valid_positions if valid_positions > 0 else 0
        
        category_data.append({
            'name': industry,
            'value': round(data['market_value'], 2),
            'percentage': percentage,
            'daily_return': f"{round(avg_return, 1)}%"
        })
    
    # 按市值排序
    category_data.sort(key=lambda x: x['value'], reverse=True)
    
    return category_data
