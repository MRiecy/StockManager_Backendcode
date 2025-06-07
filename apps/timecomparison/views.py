from django.shortcuts import render
import time
import datetime
import sys
import traceback
from django.http import JsonResponse
from rest_framework.decorators import api_view
from xtquant import xtdata
from xtquant import xtdatacenter as xtdc
from xtquant.xttrader import XtQuantTrader, XtQuantTraderCallback
from xtquant.xttype import StockAccount
from django.conf import settings
from django.db import connection
import random
import pandas as pd
import os


# Create your views here.

def ensure_xtdata_connection():
    """
    确保XtData连接已正确配置token
    返回: (bool, str) - 连接是否成功，以及错误消息（如果有）
    """
    try:
        print("正在检查并配置XtData连接...")
        
        # 设置token
        token = settings.XT_CONFIG.get('TOKEN')
        if not token:
            return False, "未配置迅投API Token"
            
        print(f"使用Token: {token[:10]}...")
        xtdc.set_token(token)
        
        # 设置连接池地址
        addr_list = settings.XT_CONFIG.get('ADDR_LIST', [])
        if addr_list:
            print(f"设置连接地址: {addr_list}")
            xtdc.set_allow_optmize_address(addr_list)
        
        # 检查连接状态
        servers = xtdata.get_quote_server_status()
        print(f"数据服务器状态: {servers}")
        
        return True, "XtData连接配置成功"
        
    except Exception as e:
        print(f"配置XtData连接失败: {str(e)}")
        return False, f"配置XtData连接失败: {str(e)}"

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


def check_api_connection():
    """
    检查与XtQuant API的连接状态
    返回: (bool, str) - 连接是否成功，以及错误消息（如果有）
    """
    try:
        print("正在检查XtQuant API连接状态...")
        
        # 查找有效的迅投路径
        valid_path = None
        all_paths = settings.XT_CONFIG.get('USERDATA_PATHS', [settings.XT_CONFIG.get('USERDATA_PATH')])
        
        for test_path in all_paths:
            if os.path.exists(test_path):
                valid_path = test_path
                print(f"找到有效的迅投路径: {valid_path}")
                break
        
        if not valid_path:
            print("未找到有效的迅投路径，已尝试以下路径:")
            for p in all_paths:
                print(f" - {p} (存在: {os.path.exists(p)})")
            return False, "未找到有效的迅投数据目录，请检查迅投安装路径"
            
        # 创建交易接口实例
        session_id = int(time.time())
        print(f"使用迅投路径: {valid_path}, 会话ID: {session_id}")
        xt_trader = XtQuantTrader(valid_path, session_id)
        callback = MyXtQuantTraderCallback()
        xt_trader.register_callback(callback)
        xt_trader.start()

        # 建立交易连接，返回 0 表示连接成功
        connect_result = xt_trader.connect()
        if connect_result != 0:
            xt_trader.stop()
            if connect_result == -1:
                error_msg = "登录失败，请检查迅投配置，确保迅投交易终端已登录"
            elif connect_result == -2:
                error_msg = "连接超时，请检查网络配置"
            else:
                error_msg = f"未知错误，错误码: {connect_result}"
            return False, error_msg
        
        # 连接成功，停止交易API
        xt_trader.stop()
        return True, "XtQuant API连接成功"
    
    except Exception as e:
        print(f"检查XtQuant API连接状态时发生异常: {str(e)}")
        return False, f"连接XtQuant API时发生异常: {str(e)}"


def get_account_positions(account_id):
    """
    获取账户的持仓股票列表
    返回: (list, bool) - 持仓股票列表，是否是模拟数据
    """
    # 默认股票，如果无法获取真实持仓将使用此股票
    default_stock = 'sh000001'  # 上证指数
    
    # 如果未提供账户ID，返回默认股票
    if not account_id:
        return [default_stock], True
    
    try:
        # 查找有效的迅投路径
        valid_path = None
        all_paths = settings.XT_CONFIG.get('USERDATA_PATHS', [settings.XT_CONFIG.get('USERDATA_PATH')])
        
        for test_path in all_paths:
            if os.path.exists(test_path):
                valid_path = test_path
                print(f"找到有效的迅投路径: {valid_path}")
                break
        
        if not valid_path:
            print("未找到有效的迅投路径")
            return [default_stock], True
            
        # 创建交易接口实例
        session_id = int(time.time())
        print(f"使用迅投路径: {valid_path}, 会话ID: {session_id}")
        xt_trader = XtQuantTrader(valid_path, session_id)
        callback = MyXtQuantTraderCallback()
        xt_trader.register_callback(callback)
        xt_trader.start()

        # 建立交易连接
        connect_result = xt_trader.connect()
        if connect_result != 0:
            print(f"连接交易接口失败，错误码: {connect_result}")
            xt_trader.stop()
            return [default_stock], True

        # 查询所有账户信息
        acc = StockAccount(account_id)

        # 订阅该账户的交易回调
        subscribe_result = xt_trader.subscribe(acc)
        if subscribe_result != 0:
            print(f"订阅账户失败，错误码: {subscribe_result}")
            xt_trader.stop()
            return [default_stock], True

        # 查询该账户的持仓信息
        positions = xt_trader.query_stock_positions(acc)
        stock_codes = []
        
        if positions:
            for pos in positions:
                stock_codes.append(pos.stock_code)
        
        # 停止交易API
        xt_trader.stop()
        
        # 如果没有持仓，则使用默认股票
        if not stock_codes:
            return [default_stock], True
        
        return stock_codes, False
    
    except Exception as e:
        print(f"获取账户持仓信息失败: {str(e)}")
        traceback.print_exc()
        return [default_stock], True


def get_historical_data(stock_codes, period='weekly'):
    """
    获取历史数据
    period: 'weekly' 或 'yearly'
    返回: (dict, bool) - 处理后的数据，是否是模拟数据
    """
    try:
        # 确保XtData连接已配置
        is_connected, error_msg = ensure_xtdata_connection()
        if not is_connected:
            print(f"XtData连接配置失败: {error_msg}")
            return None, True
        
        # 设置开始和结束时间
        end_date = datetime.datetime.now().strftime('%Y%m%d')
        
        # 根据期间类型设置开始日期
        if period == 'weekly':
            # 获取过去12周的数据
            start_date = (datetime.datetime.now() - datetime.timedelta(weeks=12)).strftime('%Y%m%d')
            time_format = '%Y-W%W'  # 周格式: 2024-W01
            num_periods = 6  # 返回6周的数据
        else:  # yearly
            # 获取过去3年的数据
            start_date = (datetime.datetime.now() - datetime.timedelta(days=365*3)).strftime('%Y%m%d')
            time_format = '%Y'  # 年格式: 2024
            num_periods = 3  # 返回3年的数据
        
        print(f"直接通过API获取历史数据，从 {start_date} 到 {end_date}")
        
        # 直接通过迅投API获取历史数据，无需下载到本地
        print("正在通过API直接获取历史数据...")
        history_data = xtdata.get_market_data_ex(
            field_list=['close', 'open', 'high', 'low', 'volume'],
            stock_list=stock_codes,
            period='1d',
            start_time=start_date,
            end_time=end_date,
            dividend_type='none',
            fill_data=True
        )
        
        # 如果获取历史数据失败
        if not history_data or stock_codes[0] not in history_data:
            print("无法获取历史数据")
            return None, True
        
        # 获取主要股票的数据
        stock_data = history_data[stock_codes[0]]
        
        # 如果没有收盘价数据
        if 'close' not in stock_data:
            print("历史数据中没有收盘价信息")
            return None, True
        
        # 处理数据
        close_prices = stock_data['close']
        dates = close_prices.index
        
        # 转换为适当的时间周期数据
        period_data = {}
        
        for i, date in enumerate(dates):
            # 转换为datetime对象
            if isinstance(date, str):
                date_obj = datetime.datetime.strptime(date, '%Y%m%d')
            else:
                date_obj = date
            
            # 根据period获取适当的时间键
            if period == 'weekly':
                # 获取日期所在的ISO周，格式为YYYY-WXX
                year, week_num, _ = date_obj.isocalendar()
                period_key = f"{year}-W{week_num:02d}"
            else:  # yearly
                # 获取年份
                period_key = date_obj.strftime('%Y')
            
            # 如果这个周期还没有数据，初始化数据
            if period_key not in period_data:
                period_data[period_key] = {
                    'dates': [],
                    'close_prices': [],
                    'total_volume': 0,
                    'high': float('-inf'),
                    'low': float('inf'),
                    'market_value': 0
                }
            
            # 添加日期和收盘价
            period_data[period_key]['dates'].append(date_obj)
            
            if i < len(close_prices):
                price = close_prices.iloc[i]
                period_data[period_key]['close_prices'].append(price)
                
                # 更新最高价和最低价
                if 'high' in stock_data and i < len(stock_data['high']):
                    period_data[period_key]['high'] = max(period_data[period_key]['high'], stock_data['high'].iloc[i])
                
                if 'low' in stock_data and i < len(stock_data['low']):
                    period_data[period_key]['low'] = min(period_data[period_key]['low'], stock_data['low'].iloc[i])
            
            # 添加成交量
            if 'volume' in stock_data and i < len(stock_data['volume']):
                period_data[period_key]['total_volume'] += stock_data['volume'].iloc[i]
        
        # 计算每个周期的市值和收益率
        result_data = []
        
        for period_key, data in period_data.items():
            if data['close_prices']:
                # 按时间排序日期
                sorted_indices = sorted(range(len(data['dates'])), key=lambda i: data['dates'][i])
                sorted_closes = [data['close_prices'][i] for i in sorted_indices]
                
                # 计算平均收盘价
                avg_price = sum(sorted_closes) / len(sorted_closes)
                
                # 假设持仓100股计算市值
                market_value = avg_price * 100
                
                # 资产总值（这里简化为市值的1.2倍）
                total_assets = market_value * 1.2
                
                # 计算收益率（使用期间的第一个和最后一个价格）
                if len(sorted_closes) > 1:
                    period_return = ((sorted_closes[-1] - sorted_closes[0]) / sorted_closes[0]) * 100
                else:
                    period_return = 0
                
                # 添加到结果列表
                result_data.append({
                    'timePeriod': period_key,
                    'totalAssets': round(total_assets, 2),
                    'marketValue': round(market_value, 2),
                    'returnRate': round(period_return, 2),
                    'growthRate': round(period_return * 0.8, 2)  # 简化的增长率计算
                })
        
        # 按时间顺序排序
        if period == 'weekly':
            # 对于周数据，我们需要特殊处理排序（YYYY-WXX格式）
            result_data.sort(key=lambda x: (int(x['timePeriod'].split('-W')[0]), int(x['timePeriod'].split('-W')[1])))
        else:
            # 对于年数据，直接按timePeriod排序即可
            result_data.sort(key=lambda x: x['timePeriod'])
        
        # 限制返回最近的num_periods个周期的数据
        if len(result_data) > num_periods:
            result_data = result_data[-num_periods:]
        
        # 获取当前资产数据（使用最新周期的数据）
        if result_data:
            latest_data = result_data[-1]
            current_data = {
                'current_total_assets': latest_data['totalAssets'],
                'current_market_value': latest_data['marketValue'],
                'current_return_rate': latest_data['returnRate']
            }
        else:
            current_data = {
                'current_total_assets': 0,
                'current_market_value': 0,
                'current_return_rate': 0
            }
        
        return {
            **current_data,
            f"{period}_data": result_data,
            'is_mock': False
        }, False
    
    except Exception as e:
        print(f"获取历史数据失败: {str(e)}")
        traceback.print_exc()
        return None, True


@api_view(['GET'])
def weekly_comparison(request):
    try:
        # 从请求参数中获取账户 ID
        account_id = request.GET.get('account_id')
        if not account_id:
            return JsonResponse({'error': '未提供账户 ID'}, status=400)
        
        print(f"获取账户 {account_id} 的每周对比数据")

        # 检查API连接状态
        api_connected, error_msg = check_api_connection()
        if not api_connected:
            print(f"API连接检查失败: {error_msg}")
            print("将使用模拟数据")
            return get_mock_weekly_comparison_data(account_id)

        # 获取账户持仓
        stock_codes, is_mock_positions = get_account_positions(account_id)
        if is_mock_positions:
            print(f"使用模拟持仓: {stock_codes}")

        # 获取历史数据并处理
        result, is_mock_data = get_historical_data(stock_codes, period='weekly')
        if is_mock_data or not result:
            print("无法获取真实历史数据，使用模拟数据")
            return get_mock_weekly_comparison_data(account_id)
        
        # 如果成功获取到真实数据，返回结果
        return JsonResponse(result)

    except Exception as e:
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)


@api_view(['GET'])
def yearly_comparison(request):
    try:
        # 从请求参数中获取账户 ID
        account_id = request.GET.get('account_id')
        if not account_id:
            return JsonResponse({'error': '未提供账户 ID'}, status=400)
        
        print(f"获取账户 {account_id} 的年度对比数据")

        # 检查API连接状态
        api_connected, error_msg = check_api_connection()
        if not api_connected:
            print(f"API连接检查失败: {error_msg}")
            print("将使用模拟数据")
            return get_mock_yearly_comparison_data(account_id)

        # 获取账户持仓
        stock_codes, is_mock_positions = get_account_positions(account_id)
        if is_mock_positions:
            print(f"使用模拟持仓: {stock_codes}")

        # 获取历史数据并处理
        result, is_mock_data = get_historical_data(stock_codes, period='yearly')
        if is_mock_data or not result:
            print("无法获取真实历史数据，使用模拟数据")
            return get_mock_yearly_comparison_data(account_id)
        
        # 如果成功获取到真实数据，返回结果
        return JsonResponse(result)

    except Exception as e:
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)


def get_mock_weekly_comparison_data(account_id):
    """
    生成模拟的每周对比数据
    """
    print(f"生成账户 {account_id} 的模拟每周对比数据")
    
    # 当前日期
    current_date = datetime.datetime.now()
    
    # 生成模拟数据
    weekly_data = []
    
    # 基础总资产和市值
    base_total_assets = random.uniform(500000, 1000000)  # 基础总资产50-100万
    base_market_value = base_total_assets * 0.8  # 基础市值大约是总资产的80%
    
    # 基础收益率
    base_return_rate = random.uniform(2, 5)  # 2%-5%
    
    # 按周生成数据（当前周向前推6周）
    for i in range(6):
        # 计算每周的日期（向前推i周）
        week_date = current_date - datetime.timedelta(weeks=i)
        year, week_num, _ = week_date.isocalendar()
        week_str = f"{year}-W{week_num:02d}"  # 格式：2024-W01
        
        # 每周递减一些资产和市值
        week_factor = 1 - (i * 0.05)  # 本周是1，上周是0.95，上上周是0.9
        
        total_assets = base_total_assets * week_factor
        market_value = base_market_value * week_factor
        
        # 收益率也随着时间变化
        return_rate = base_return_rate * (1 - i * 0.15)
        
        # 增长率（与上一周相比）
        prev_return_rate = base_return_rate * (1 - (i+1) * 0.15) if i < 5 else 0
        growth_rate = return_rate - prev_return_rate
        
        weekly_data.append({
            'timePeriod': week_str,
            'totalAssets': round(total_assets, 2),
            'marketValue': round(market_value, 2),
            'returnRate': round(return_rate, 2),
            'growthRate': round(growth_rate, 2)
        })
    
    # 按照时间顺序排序（从早到晚）
    weekly_data.reverse()
    
    # 构建返回数据
    result = {
        'current_total_assets': round(base_total_assets, 2),
        'current_market_value': round(base_market_value, 2),
        'current_return_rate': round(base_return_rate, 2),
        'weekly_data': weekly_data,
        'is_mock': True
    }
    
    return JsonResponse(result)


def get_mock_yearly_comparison_data(account_id):
    """
    生成模拟的年度对比数据
    """
    print(f"生成账户 {account_id} 的模拟年度对比数据")
    
    # 当前年份
    current_year = datetime.datetime.now().year
    
    # 生成模拟数据
    yearly_data = []
    
    # 基础总资产和市值
    base_total_assets = random.uniform(3000000, 5000000)  # 基础总资产300-500万
    base_market_value = base_total_assets * 0.8  # 基础市值大约是总资产的80%
    
    # 基础收益率
    base_return_rate = random.uniform(5, 15)  # 5%-15%
    
    # 按年份生成数据（当前年份向前推3年）
    for i in range(3):
        year = current_year - i
        
        # 每年递减一些资产和市值
        year_factor = 1 - (i * 0.1)  # 今年是1，去年是0.9，前年是0.8
        
        total_assets = base_total_assets * year_factor
        market_value = base_market_value * year_factor
        
        # 收益率也随着时间变化
        return_rate = base_return_rate * (1 - i * 0.2)
        
        # 增长率（与上一年相比）
        prev_return_rate = base_return_rate * (1 - (i+1) * 0.2) if i < 2 else 0
        growth_rate = return_rate - prev_return_rate
        
        yearly_data.append({
            'timePeriod': str(year),
            'totalAssets': round(total_assets, 2),
            'marketValue': round(market_value, 2),
            'returnRate': round(return_rate, 2),
            'growthRate': round(growth_rate, 2)
        })
    
    # 按照时间顺序排序（从早到晚）
    yearly_data.reverse()
    
    # 构建返回数据
    result = {
        'current_total_assets': round(base_total_assets, 2),
        'current_market_value': round(base_market_value, 2),
        'current_return_rate': round(base_return_rate, 2),
        'yearly_data': yearly_data,
        'is_mock': True
    }
    
    return JsonResponse(result)
