import time
import datetime
import sys
import traceback
import numpy as np
import pandas as pd
from django.http import JsonResponse
from xtquant import xtdata
from xtquant.xttrader import XtQuantTrader, XtQuantTraderCallback
from xtquant.xttype import StockAccount
from datetime import datetime, timedelta
from .utils import (
    get_total_shares, 
    get_category_start_value, 
    get_account_history,
    get_total_assets
)
import os


# 定义交易回调类
class MyXtQuantTraderCallback(XtQuantTraderCallback):
    def on_disconnected(self):
        print(datetime.now(), '连接断开回调')

    def on_stock_order(self, order):
        print(datetime.now(), '委托回调 投资备注', order.order_remark)

    def on_stock_trade(self, trade):
        print(datetime.now(), '成交回调', trade.order_remark,
              f"委托方向(48买 49卖) {trade.offset_flag} 成交价格 {trade.traded_price} 成交数量 {trade.traded_volume}")

    def on_order_error(self, order_error):
        print(f"委托报错回调 {order_error.order_remark} {order_error.error_msg}")

    def on_cancel_error(self, cancel_error):
        print(datetime.now(), sys._getframe().f_code.co_name)

    def on_order_stock_async_response(self, response):
        print(f"异步委托回调 投资备注: {response.order_remark}")

    def on_cancel_order_stock_async_response(self, response):
        print(datetime.now(), sys._getframe().f_code.co_name)

    def on_account_status(self, status):
        print(datetime.now(), sys._getframe().f_code.co_name)


# 初始化交易接口
def init_xt_trader():
    try:
        path = r'D:\迅投极速交易终端 睿智融科版\userdata'

        # 检查路径是否存在
        if not os.path.exists(path):
            print(f"交易数据路径不存在: {path}")
            # 如果路径不存在，直接返回模拟交易接口
            from .mock_trader import MockXtTrader
            return MockXtTrader()
            
        session_id = int(time.time())
        xt_trader = XtQuantTrader(path, session_id)
        callback = MyXtQuantTraderCallback()
        xt_trader.register_callback(callback)
        xt_trader.start()
        connect_result = xt_trader.connect()
        if connect_result != 0:
            print(f"连接交易接口失败，错误码: {connect_result}")
            raise Exception(f'连接交易接口失败，错误码: {connect_result}')
        return xt_trader
    except Exception as e:
        print(f"初始化交易接口错误: {str(e)}")
        # 返回模拟交易接口
        from .mock_trader import MockXtTrader
        return MockXtTrader()


# 计算最大回撤
def calculate_max_drawdown(prices):
    if len(prices) == 0:
        return 0
    cumulative_max = np.maximum.accumulate(prices)
    drawdowns = (cumulative_max - prices) / cumulative_max
    max_drawdown = np.max(drawdowns) if len(drawdowns) > 0 else 0
    return max_drawdown * 100  # 转换为百分比


# 计算收益率
def calculate_return_rate(start_value, end_value, period_type='simple'):
    if start_value == 0:
        return 0
    if period_type == 'simple':
        return (end_value - start_value) / start_value * 100
    # elif period_type == 'annual':
    #     return ((end_value / start_value) ** (365 / (end_date - start_date).days) - 1) * 100
    # elif period_type == 'compound':
    #     return ((end_value / start_value) ** (1 / ((end_date - start_date).days / 365)) - 1) * 100
    return 0


def get_asset_category_data(request):
    try:
        xt_trader = init_xt_trader()
        accounts = xt_trader.query_account_infos()
        category_data = []

        asset_categories = {
            'stock': '股票',
            'credit': '信用',
            'futures': '期货',
            'futures_options': '期货期权',
            'stock_options': '股票期权',
            'sh_hk_connect': '沪港通',
            'sz_hk_connect': '深港通'
        }

        for acc in accounts:
            asset = xt_trader.query_stock_asset(acc)
            if asset is None:
                continue

            positions = xt_trader.query_stock_positions(acc)
            if not positions:
                continue

            # 获取账户总资产，防止除以零错误
            total_asset = getattr(asset, 'total_asset', 0)
            if total_asset == 0:
                total_asset = 1  # 设置一个默认值

            # 初始化各类别数据
            category_details = {
                k: {
                    'market_value': 0,
                    'positions': [],
                    'total_value': 0,
                    'return_rate': 0
                } for k in asset_categories.keys()
            }

            # 计算各类资产的市场额
            for pos in positions:
                # 根据持仓类型分类
                category = 'stock'  # 默认为股票
                if pos.stock_code.endswith('.SH') or pos.stock_code.endswith('.SZ'):
                    category = 'stock'
                elif pos.stock_code.startswith('H') and pos.stock_code.endswith('.HK'):
                    if pos.stock_code.endswith('.SH.HK'):
                        category = 'sh_hk_connect'
                    else:
                        category = 'sz_hk_connect'
                elif pos.stock_code.startswith('10') or pos.stock_code.startswith('11'):
                    category = 'futures'
                elif pos.stock_code.startswith('9'):
                    category = 'stock_options'
                # 这里可以继续添加其他分类逻辑...

                # 确保position_value有值
                position_value = getattr(pos, 'market_value', 0)
                if position_value == 0 and hasattr(pos, 'volume') and hasattr(pos, 'current_price'):
                    position_value = pos.volume * pos.current_price

                # 更新类别数据
                if category in category_details:
                    total_shares_value = get_total_shares(pos.stock_code)
                    current_price = getattr(pos, 'current_price', 0)
                    market_value = current_price * total_shares_value
                    category_details[category]['market_value'] += market_value
                    category_details[category]['positions'].append(pos.stock_code)
                    category_details[category]['total_value'] += position_value

            # 计算收益率
            for category, data in category_details.items():
                if data['total_value'] > 0:
                    # 获取期初价值
                    start_value = get_category_start_value(acc, category)
                    return_rate = calculate_return_rate(start_value, data['total_value'], 'simple')

                    # 计算市场份额时防止除以零
                    market_share = (data["market_value"] / total_asset * 100) if total_asset > 0 else 0

                    category_data.append({
                        'category': asset_categories[category],
                        'totalAssets': data['total_value'],
                        'returnRate': f'{return_rate:.2f}%',
                        'marketShare': f'{market_share:.2f}%',
                        'marketValue': data['market_value']
                    })

        return JsonResponse({'categoryData': category_data})
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)


def get_time_data(request):
    try:
        period = request.GET.get('period', 'weekly')
        xt_trader = init_xt_trader()
        accounts = xt_trader.query_account_infos()
        time_data = []

        for acc in accounts:
            # 获取历史资产数据
            history_data = get_account_history(acc, period)

            if not history_data:
                # 没有历史数据时生成模拟数据
                if period == 'weekly':
                    # 生成周度数据
                    for i in range(1, 5):  # 生成4周数据
                        date = (datetime.now() - timedelta(weeks=i)).strftime('%Y-%m-%d')
                        total_assets = 1000000 * (1 + 0.02 * i)  # 模拟增长
                        return_rate = 2.0 * i
                        market_value = total_assets * 0.9  # 假设90%是市值
                        growth_rate = 2.0 * i  # 同收益率简化处理

                        time_data.append({
                            'timePeriod': f'第{i}周 ({date})',
                            'totalAssets': total_assets,
                            'returnRate': f'{return_rate:.2f}%',
                            'growthRate': f'{growth_rate:.2f}%',
                            'marketValue': market_value
                        })
                else:  # yearly
                    # 生成年度数据
                    for i in range(1, 6):  # 生成5年数据
                        year = datetime.now().year - i
                        total_assets = 1000000 * (1 + 0.1 * i)  # 模拟年增长10%
                        return_rate = 10.0 * i
                        market_value = total_assets * 0.9
                        growth_rate = 10.0 * i  # 同收益率简化处理

                        time_data.append({
                            'timePeriod': f'{year}年',
                            'totalAssets': total_assets,
                            'returnRate': f'{return_rate:.2f}%',
                            'growthRate': f'{growth_rate:.2f}%',
                            'marketValue': market_value
                        })
            else:
                # 处理真实历史数据
                for record in history_data:
                    start_value = record.get('start_value', 0)
                    end_value = record.get('end_value', 0)
                    return_rate = calculate_return_rate(start_value, end_value, period) if start_value > 0 else 0
                    
                    # 计算增长率（简化为与收益率相同）
                    growth_rate = return_rate
                    
                    time_data.append({
                        'timePeriod': record['period'],
                        'totalAssets': record['total_assets'],
                        'returnRate': f"{return_rate:.2f}%",
                        'growthRate': f"{growth_rate:.2f}%",
                        'marketValue': record['market_value']
                    })

        # 按时间排序
        if period == 'weekly':
            time_data.sort(key=lambda x: x['timePeriod'], reverse=True)
        else:  # yearly
            time_data.sort(key=lambda x: x['timePeriod'], reverse=True)

        return JsonResponse({'timeData': time_data})
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)


def get_region_data(request):
    try:
        xt_trader = init_xt_trader()
        accounts = xt_trader.query_account_infos()
        region_data = []

        regions = {
            'SH': '上海',
            'SZ': '深圳',
            'HK': '香港',
            'US': '美国'
        }

        # 计算总资产，用于后续计算投资率
        total_assets = 0
        for acc in accounts:
            asset = xt_trader.query_stock_asset(acc)
            if asset and hasattr(asset, 'total_asset'):
                total_assets += asset.total_asset

        # 如果总资产为0，设置一个默认值避免除以零错误
        if total_assets == 0:
            total_assets = 1

        for acc in accounts:
            positions = xt_trader.query_stock_positions(acc)
            if not positions:
                continue

            for pos in positions:
                # 确定地区
                region = '其他'
                exchange = 'OTHER'
                
                if pos.stock_code.endswith('.SH'):
                    region = '上海'
                    exchange = 'SH'
                elif pos.stock_code.endswith('.SZ'):
                    region = '深圳'
                    exchange = 'SZ'
                elif pos.stock_code.endswith('.HK'):
                    region = '香港'
                    exchange = 'HK'
                elif pos.stock_code.endswith('.US'):
                    region = '美国'
                    exchange = 'US'

                # 计算最大回撤
                stock_code = pos.stock_code
                max_drawdown = 0
                return_rate = 0
                
                try:
                    # 尝试获取历史价格数据计算回撤和收益率
                    start_time = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')
                    end_time = datetime.now().strftime('%Y%m%d')

                    price_data = xtdata.get_market_data(
                        stock_list=[stock_code],
                        period='1d',
                        start_time=start_time,
                        end_time=end_time,
                        dividend_type='none'
                    )

                    if price_data and 'close' in price_data and stock_code in price_data['close']:
                        close_prices = price_data['close'][stock_code]
                        if len(close_prices) > 0:
                            max_drawdown = calculate_max_drawdown(close_prices)
                            start_price = close_prices[0]
                            end_price = close_prices[-1]
                            return_rate = calculate_return_rate(start_price, end_price, 'simple')
                except Exception as e:
                    print(f"获取{stock_code}价格数据出错: {str(e)}")

                # 确保market_value有值
                market_value = getattr(pos, 'market_value', 0)
                if not market_value and hasattr(pos, 'volume') and hasattr(pos, 'current_price'):
                    market_value = pos.volume * pos.current_price

                region_data.append({
                    'region': region,
                    'exchange': exchange,
                    'stockCode': pos.stock_code,
                    'marketValue': market_value,
                    'maxDrawdown': f'{max_drawdown:.2f}%',
                    'returnRate': f'{return_rate:.2f}%'
                })

        # 按地区汇总
        region_summary = {}
        for data in region_data:
            region = data['region']
            if region not in region_summary:
                region_summary[region] = {
                    'totalAssets': 0,
                    'maxDrawdowns': [],
                    'returnRates': [],
                    'positions': []
                }
            region_summary[region]['totalAssets'] += data['marketValue']
            # 转换百分比字符串为浮点数
            max_drawdown = float(data['maxDrawdown'].replace('%', '')) if data['maxDrawdown'] else 0
            return_rate = float(data['returnRate'].replace('%', '')) if data['returnRate'] else 0
            
            region_summary[region]['maxDrawdowns'].append(max_drawdown)
            region_summary[region]['returnRates'].append(return_rate)
            region_summary[region]['positions'].append(data['stockCode'])

        # 计算平均值
        result = []
        
        for region, summary in region_summary.items():
            avg_drawdown = np.mean(summary['maxDrawdowns']) if summary['maxDrawdowns'] else 0
            avg_return = np.mean(summary['returnRates']) if summary['returnRates'] else 0
            investment_rate = (summary["totalAssets"] / total_assets) * 100

            result.append({
                'region': region,
                'totalAssets': summary['totalAssets'],
                'returnRate': f'{avg_return:.2f}%',
                'maxDrawdown': f'{avg_drawdown:.2f}%',
                'investmentRate': f'{investment_rate:.2f}%'
            })

        return JsonResponse({'regionData': result})
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)


def get_strategies(request):
    """
    获取交易策略列表及其执行情况
    """
    try:
        # 模拟数据，实际应从数据库获取
        strategies = [
            {
                'id': 1,
                'name': '量化价值策略',
                'description': '基于PE、PB等基本面指标的价值投资策略',
                'status': 'active',
                'returnRate': '8.5%',
                'maxDrawdown': '5.2%',
                'lastExecuted': '2023-06-15'
            },
            {
                'id': 2,
                'name': '趋势跟踪策略',
                'description': '基于均线交叉和动量指标的趋势跟踪策略',
                'status': 'inactive',
                'returnRate': '12.3%',
                'maxDrawdown': '9.8%',
                'lastExecuted': '2023-05-21'
            },
            {
                'id': 3,
                'name': '均值回归策略',
                'description': '基于价格偏离均值的回归交易策略',
                'status': 'active',
                'returnRate': '6.7%',
                'maxDrawdown': '4.5%',
                'lastExecuted': '2023-06-10'
            }
        ]
        
        return JsonResponse({'strategies': strategies})
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)


def get_execution_result(request):
    """
    获取策略执行结果
    """
    try:
        strategy_id = request.GET.get('strategy_id')
        
        # 模拟数据，实际应从数据库获取
        execution_results = [
            {
                'id': 1,
                'strategy_id': '1',
                'date': '2023-06-15',
                'action': '买入',
                'stockCode': '600000.SH',
                'price': 10.25,
                'volume': 2000,
                'amount': 20500,
                'status': '已成交'
            },
            {
                'id': 2,
                'strategy_id': '1',
                'date': '2023-06-14',
                'action': '卖出',
                'stockCode': '000001.SZ',
                'price': 15.75,
                'volume': 1500,
                'amount': 23625,
                'status': '已成交'
            },
            {
                'id': 3,
                'strategy_id': '2',
                'date': '2023-05-21',
                'action': '买入',
                'stockCode': '601318.SH',
                'price': 45.80,
                'volume': 500,
                'amount': 22900,
                'status': '已成交'
            }
        ]
        
        # 如果指定了策略ID，则过滤结果
        if strategy_id:
            execution_results = [r for r in execution_results if r['strategy_id'] == strategy_id]
        
        return JsonResponse({'executionResults': execution_results})
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)
