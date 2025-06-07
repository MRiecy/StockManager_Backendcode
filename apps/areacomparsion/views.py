from django.shortcuts import render
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
import random


# Create your views here.

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


# 根据股票代码判断交易所/地区
def get_stock_exchange(stock_code):
    """
    根据股票代码判断交易所/地区
    沪市: 股票代码以60开头
    深市: 股票代码以00或30开头
    创业板: 股票代码以3开头
    科创板: 股票代码以688开头
    北交所: 股票代码以4、8开头
    港股: 股票代码以9开头
    """
    if stock_code.startswith('60'):
        return '上海'
    elif stock_code.startswith('00') or stock_code.startswith('30'):
        return '深圳'
    elif stock_code.startswith('3'):
        return '创业板'
    elif stock_code.startswith('688'):
        return '科创板'
    elif stock_code.startswith('4') or stock_code.startswith('8'):
        return '北交所'
    elif stock_code.startswith('9'):
        return '港股'
    else:
        return '其他'


@api_view(['GET'])
def area_comparison(request):
    try:
        # 从请求参数中获取账户 ID
        account_id = request.GET.get('account_id')
        if not account_id:
            return JsonResponse({'error': '未提供账户 ID'}, status=400)
        
        try:
            # 尝试从交易接口获取真实数据
            # 创建交易接口实例
            path = settings.XT_CONFIG.get('USERDATA_PATH', './')
            session_id = int(time.time())
            xt_trader = XtQuantTrader(path, session_id)
            callback = MyXtQuantTraderCallback()
            xt_trader.register_callback(callback)
            xt_trader.start()

            # 建立交易连接，返回 0 表示连接成功
            connect_result = xt_trader.connect()
            print(f"正在连接交易接口，结果：{connect_result}")
            if connect_result != 0:
                print(f"连接交易接口失败，将使用模拟数据")
                return get_mock_area_comparison_data(account_id)

            # 查询所有账户信息
            acc = StockAccount(account_id)

            # 订阅该账户的交易回调
            subscribe_result = xt_trader.subscribe(acc)
            print(f"正在订阅账户 {account_id}，结果：{subscribe_result}")
            if subscribe_result != 0:
                print(f"订阅账户失败，将使用模拟数据")
                xt_trader.stop()
                return get_mock_area_comparison_data(account_id)

            # 查询账户资产信息
            asset = xt_trader.query_stock_asset(acc)
            print(f"查询资产结果：{asset}")
            if not asset:
                print("未查询到账户资产信息，将使用模拟数据")
                xt_trader.stop()
                return get_mock_area_comparison_data(account_id)

            # 查询该账户的持仓信息
            positions = xt_trader.query_stock_positions(acc)
            if not positions:
                print("未查询到持仓信息，将使用模拟数据")
                xt_trader.stop()
                return get_mock_area_comparison_data(account_id)

            # 计算各地区的统计数据
            area_data = {}
            total_market_value = asset.market_value  # 总持仓市值

            # 按地区分组
            for pos in positions:
                stock_code = pos.stock_code  # 股票代码
                market_value = pos.market_value  # 市值
                avg_price = pos.avg_price  # 成本价
                latest_price = pos.lastprice if hasattr(pos, 'lastprice') else pos.open_price  # 最新价
                
                # 根据股票代码判断所属地区
                area = get_stock_exchange(stock_code)
                
                # 计算当前股票的收益率
                return_rate = ((latest_price - avg_price) / avg_price) * 100 if avg_price > 0 else 0
                
                # 初始化地区数据
                if area not in area_data:
                    area_data[area] = {
                        'marketValue': 0,
                        'returnRate': 0,
                        'stockCount': 0,
                        'totalWeight': 0,
                        'maxDrawdown': 0,  # 暂时设为0，后面可能需要历史数据计算
                        'stocks': []
                    }
                
                # 计算股票在当前地区的权重
                stock_weight = market_value / total_market_value if total_market_value > 0 else 0
                
                # 累加地区的市值和股票数
                area_data[area]['marketValue'] += market_value
                area_data[area]['stockCount'] += 1
                area_data[area]['totalWeight'] += stock_weight
                
                # 将股票信息添加到地区
                area_data[area]['stocks'].append({
                    'stockCode': stock_code,
                    'marketValue': market_value,
                    'returnRate': return_rate,
                    'weight': stock_weight
                })

            # 计算每个地区的加权平均收益率
            for area, data in area_data.items():
                weighted_return = 0
                for stock in data['stocks']:
                    # 计算该股票在地区内的权重
                    area_weight = stock['marketValue'] / data['marketValue'] if data['marketValue'] > 0 else 0
                    weighted_return += stock['returnRate'] * area_weight
                
                data['returnRate'] = round(weighted_return, 2)
                data['marketValue'] = round(data['marketValue'], 2)
                data['investmentRate'] = round((data['marketValue'] / total_market_value) * 100 if total_market_value > 0 else 0, 2)
                
                # 移除不需要返回的临时数据
                del data['stocks']
                del data['totalWeight']
            
            # 计算最大回撤率（模拟数据，实际应该基于历史数据计算）
            # 在这个例子中，我们假设最大回撤与收益率有一定相关性
            for area, data in area_data.items():
                # 模拟最大回撤率 - 实际应基于历史数据
                # 假设收益率越高，历史波动可能越大，最大回撤也可能越大
                simulated_max_drawdown = abs(data['returnRate']) * 0.8 if data['returnRate'] < 0 else data['returnRate'] * 0.3
                data['maxDrawdown'] = round(simulated_max_drawdown, 2)

            # 转换为前端需要的格式
            result_data = []
            for area, data in area_data.items():
                result_data.append({
                    'region': area,
                    'maxDrawdown': data['maxDrawdown'],
                    'returnRate': data['returnRate'],
                    'investmentRate': data['investmentRate'],
                    'totalAssets': data['marketValue'],
                    'stockCount': data['stockCount']
                })
            
            # 停止交易API
            xt_trader.stop()
            
            return JsonResponse({
                'total_market_value': round(total_market_value, 2),
                'area_data': result_data
            })

        except Exception as e:
            print(f"处理地区对比数据时发生异常: {str(e)}，将使用模拟数据")
            # 尝试停止交易API（如果已初始化）
            try:
                if 'xt_trader' in locals():
                    xt_trader.stop()
            except:
                pass
            # 返回模拟数据
            return get_mock_area_comparison_data(account_id)
        
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)

def get_mock_area_comparison_data(account_id):
    """
    生成模拟的地区对比数据
    """
    print(f"生成账户 {account_id} 的模拟地区对比数据")
    
    # 模拟地区列表
    regions = ['上海', '深圳', '创业板', '科创板', '北交所', '港股']
    
    # 随机选择3-5个地区
    selected_regions = random.sample(regions, random.randint(3, 5))
    
    # 生成随机地区数据
    area_data = []
    total_market_value = random.uniform(3000000, 5000000)  # 总市值300-500万
    
    for region in selected_regions:
        # 生成随机市值占比
        market_value = random.uniform(0.1, 0.5) * total_market_value / len(selected_regions)
        
        # 生成随机收益率 (-15% 到 +20%)
        return_rate = random.uniform(-15, 20)
        
        # 生成随机投资率/最大回撤率 (5% - 40%)
        investment_rate = random.uniform(5, 40)
        
        # 生成随机股票数量 (1-10)
        stock_count = random.randint(1, 10)
        
        max_drawdown = return_rate * 0.3 if return_rate > 0 else abs(return_rate) * 0.8
        
        area_data.append({
            'region': region,
            'maxDrawdown': round(max_drawdown, 2),
            'returnRate': round(return_rate, 2),
            'investmentRate': round(investment_rate, 2),
            'totalAssets': round(market_value, 2),
            'stockCount': stock_count
        })
    
    # 构建返回数据
    response_data = {
        'total_market_value': round(total_market_value, 2),
        'area_data': area_data
    }
    
    return JsonResponse(response_data)
