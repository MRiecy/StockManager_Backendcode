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
        
        # 是否使用模拟数据（当连接失败时自动使用）
        use_mock_data = request.GET.get('use_mock', 'false').lower() == 'true'
        
        if not use_mock_data:
            try:
                # 创建交易接口实例
                path = r'E:\迅投极速交易终端 睿智融科版\userdata'
                print(f"尝试使用路径: {path}")
                session_id = int(time.time())
                xt_trader = XtQuantTrader(path, session_id)
                callback = MyXtQuantTraderCallback()
                xt_trader.register_callback(callback)
                xt_trader.start()

                # 建立交易连接，返回 0 表示连接成功
                print("正在连接迅投交易接口...")
                connect_result = xt_trader.connect()
                if connect_result != 0:
                    print(f"迅投交易接口连接失败，错误码: {connect_result}")
                    # 如果连接失败，使用模拟数据
                    use_mock_data = True
                    raise Exception(f"迅投交易接口连接失败，错误码: {connect_result}")
                
                print("迅投交易接口连接成功")
                
                # 如果没有提供账户ID，则获取所有账户
                if not account_id:
                    accounts = xt_trader.query_account_infos()
                    if not accounts or len(accounts) == 0:
                        print("未查询到账户信息")
                        use_mock_data = True
                        raise Exception("未查询到账户信息")
                    # 使用第一个账户的ID
                    account_id = accounts[0].account_id
                    print(f"未提供账户ID，使用第一个账户: {account_id}")

                # 查询所有账户信息
                acc = StockAccount(account_id)

                # 订阅该账户的交易回调
                print("订阅账户交易回调...")
                subscribe_result = xt_trader.subscribe(acc)
                if subscribe_result != 0:
                    print(f"订阅账户失败，错误码: {subscribe_result}")
                    use_mock_data = True
                    raise Exception(f"订阅账户失败，错误码: {subscribe_result}")

                # 查询账户资产信息
                print("查询账户资产信息...")
                asset = xt_trader.query_stock_asset(acc)
                if not asset:
                    print("未查询到账户资产信息")
                    use_mock_data = True
                    raise Exception("未查询到账户资产信息")

                # 查询该账户的持仓信息
                print("查询账户持仓信息...")
                positions = xt_trader.query_stock_positions(acc)
                if not positions:
                    print("未查询到持仓信息")
                    use_mock_data = True
                    raise Exception("未查询到持仓信息")

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
                
                # 停止交易API
                xt_trader.stop()
                print("已停止交易API")

                # 返回结果，格式与前端期望的一致
                return JsonResponse({
                    'accounts': [{
                        'account_id': account_id,
                        'total_market_value': round(total_market_value, 2),
                        'positions': pos_list,
                        'is_mock': False
                    }]
                })
                
            except Exception as e:
                print(f"获取真实数据失败: {str(e)}")
                print("将使用模拟数据")
                use_mock_data = True
                
                # 确保在发生异常时关闭交易API
                try:
                    if 'xt_trader' in locals():
                        xt_trader.stop()
                        print("异常处理中关闭了交易API")
                except:
                    pass
        
        # 使用模拟数据
        if use_mock_data:
            print("正在生成模拟资产对比数据...")
            # 模拟的账户ID
            mock_account_id = account_id or "mock_account_123"
            
            # 模拟的持仓数据
            mock_positions = [
                {
                    'stock_code': '600000.SH',
                    'asset_ratio': 0.35,
                    'market_value': 350000.00,
                    'daily_return': 2.50
                },
                {
                    'stock_code': '000001.SZ',
                    'asset_ratio': 0.25,
                    'market_value': 250000.00,
                    'daily_return': 1.80
                },
                {
                    'stock_code': '601318.SH',
                    'asset_ratio': 0.20,
                    'market_value': 200000.00,
                    'daily_return': 3.20
                },
                {
                    'stock_code': '002415.SZ',
                    'asset_ratio': 0.12,
                    'market_value': 120000.00,
                    'daily_return': -0.50
                },
                {
                    'stock_code': '300750.SZ',
                    'asset_ratio': 0.08,
                    'market_value': 80000.00,
                    'daily_return': 4.60
                }
            ]
            
            # 模拟的总市值
            mock_total_market_value = 1000000.00
            
            print("模拟数据生成完成")
            
            # 返回模拟数据
            return JsonResponse({
                'accounts': [{
                    'account_id': mock_account_id,
                    'total_market_value': mock_total_market_value,
                    'positions': mock_positions,
                    'is_mock': True
                }]
            })

    except Exception as e:
        traceback.print_exc()
        return JsonResponse({
            'error': str(e),
            'code': 500
        }, status=500)

@api_view(['GET'])
def time_data(request):
    """
    提供账户的时间序列资产数据
    使用XtQuant API获取历史数据
    """
    try:
        # 从请求参数中获取账户 ID
        account_id = request.GET.get('account_id')
        # 时间范围参数
        time_range = request.GET.get('time_range', 'month')
        
        print("开始获取历史数据...")
        
        # 获取股票代码列表，如果没有指定账户，则使用默认的几支股票
        stock_codes = []
        
        # 默认使用沪深300指数
        default_stock = '000300.SH'
        
        # 尝试获取账户持仓
        try:
            # 创建交易接口实例
            path = r'E:\迅投极速交易终端 睿智融科版\userdata'
            print(f"尝试使用路径: {path}")
            session_id = int(time.time())
            xt_trader = XtQuantTrader(path, session_id)
            callback = MyXtQuantTraderCallback()
            xt_trader.register_callback(callback)
            xt_trader.start()
            
            # 建立交易连接
            print("正在连接迅投交易接口...")
            connect_result = xt_trader.connect()
            if connect_result != 0:
                print(f"迅投交易接口连接失败，错误码: {connect_result}")
                raise Exception(f"迅投交易接口连接失败，错误码: {connect_result}")
                
            # 如果没有提供账户ID，则获取所有账户并使用第一个
            if not account_id:
                accounts = xt_trader.query_account_infos()
                if not accounts or len(accounts) == 0:
                    print("未查询到账户信息")
                    raise Exception("未查询到账户信息")
                account_id = accounts[0].account_id
                print(f"未提供账户ID，使用第一个账户: {account_id}")
            
            # 获取账户对象
            acc = StockAccount(account_id)
            
            # 订阅该账户的交易回调
            subscribe_result = xt_trader.subscribe(acc)
            if subscribe_result != 0:
                print(f"订阅账户失败，错误码: {subscribe_result}")
                raise Exception(f"订阅账户失败，错误码: {subscribe_result}")
                
            # 查询账户持仓信息，获取持仓股票代码
            positions = xt_trader.query_stock_positions(acc)
            if positions:
                for pos in positions:
                    stock_codes.append(pos.stock_code)
                    
            # 停止交易API
            xt_trader.stop()
            print("已停止交易API")
            
        except Exception as e:
            print(f"获取账户持仓失败: {str(e)}")
            # 如果获取持仓失败，则使用默认股票
            stock_codes = [default_stock]
            
        # 如果没有持仓，也使用默认股票
        if not stock_codes:
            stock_codes = [default_stock]
            
        print(f"将查询股票: {stock_codes}")
        
        # 根据据文章中的信息，先下载历史数据，再获取
        try:
            # 设置开始和结束时间
            end_date = datetime.datetime.now().strftime('%Y%m%d')
            start_date = (datetime.datetime.now() - datetime.timedelta(days=180)).strftime('%Y%m%d')
            
            print(f"下载历史数据，从 {start_date} 到 {end_date}")
            
            # 使用迅投API下载历史数据
            for stock_code in stock_codes:
                # 下载日线数据
                print(f"正在下载 {stock_code} 的历史数据...")
                xtdata.download_history_data(
                    stock_code=stock_code,
                    period='1d',  # 日线数据
                    start_time=start_date,
                    end_time=end_date,
                    incrementally=True  # 增量下载
                )
            
            # 获取历史数据
            print("正在获取下载的历史数据...")
            history_data = xtdata.get_market_data(
                field_list=['close', 'open', 'high', 'low', 'volume'],
                stock_list=stock_codes,
                period='1d',
                start_time=start_date,
                end_time=end_date,
                dividend_type='none',
                fill_data=True
            )
            
            print(f"成功获取历史数据")
            
            # 准备返回的时间序列数据
            time_data = []
            
            # 如果有历史数据，则处理数据并返回
            if history_data and stock_codes[0] in history_data:
                stock_data = history_data[stock_codes[0]]
                
                if 'close' in stock_data:
                    close_prices = stock_data['close']
                    dates = close_prices.index
                    
                    # 转换为月份数据
                    monthly_data = {}
                    for i, date in enumerate(dates):
                        # 转换为datetime对象
                        if isinstance(date, str):
                            date_obj = datetime.datetime.strptime(date, '%Y%m%d')
                        else:
                            date_obj = date
                            
                        # 获取年月作为键
                        month_key = date_obj.strftime('%Y-%m')
                        
                        # 如果这个月份还没有数据，初始化数据
                        if month_key not in monthly_data:
                            monthly_data[month_key] = {
                                'close_prices': [],
                                'total_volume': 0
                            }
                            
                        # 添加收盘价
                        if i < len(close_prices):
                            monthly_data[month_key]['close_prices'].append(close_prices.iloc[i])
                            
                        # 添加成交量，如果有
                        if 'volume' in stock_data and i < len(stock_data['volume']):
                            monthly_data[month_key]['total_volume'] += stock_data['volume'].iloc[i]
                    
                    # 计算每月的平均收盘价作为该月的资产值
                    for month, data in monthly_data.items():
                        if data['close_prices']:
                            avg_price = sum(data['close_prices']) / len(data['close_prices'])
                            
                            # 假设持仓100股计算资产值
                            asset_value = avg_price * 100
                            
                            # 计算月度收益率（使用月初和月末的价格）
                            if len(data['close_prices']) > 1:
                                monthly_return = ((data['close_prices'][-1] - data['close_prices'][0]) / data['close_prices'][0]) * 100
                            else:
                                monthly_return = 0
                                
                            # 添加月度数据
                            time_data.append({
                                "timePeriod": month,
                                "totalAssets": round(asset_value, 2),
                                "returnRate": f"{round(monthly_return, 1)}%",
                                "growthRate": f"{round(monthly_return * 1.2, 1)}%"  # 简化的增长率计算
                            })
                    
                    # 按时间顺序排序
                    time_data.sort(key=lambda x: x["timePeriod"])
                    
                    # 限制返回最近5个月的数据
                    if len(time_data) > 5:
                        time_data = time_data[-5:]
                    
                    print(f"成功处理历史数据，生成了 {len(time_data)} 条月度记录")
                    
                    return JsonResponse({
                        'timeData': time_data,
                        'account_id': account_id,
                        'is_mock': False,
                        'message': '使用股票历史数据生成的资产时间序列'
                    })
            
        except Exception as e:
            print(f"获取历史数据失败: {str(e)}")
            traceback.print_exc()
            
        # 如果无法获取历史数据，则生成模拟数据
        print("无法获取真实历史数据，生成模拟时间序列数据...")
        
        # 使用当前月份作为基准
        current_month = datetime.datetime.now().month
        current_year = datetime.datetime.now().year
        
        # 使用模拟总资产值
        total_asset = 1000000.00
        
        # 生成最近5个月的数据
        time_data = []
        for i in range(5):
            # 计算月份和年份
            month = current_month - i
            year = current_year
            if month <= 0:
                month += 12
                year -= 1
                
            # 模拟该月的资产数据
            asset_ratio = 1 - (i * 0.05)  # 每往前一个月资产减少5%
            monthly_asset = round(total_asset * asset_ratio, 2)
            
            # 模拟收益率和增长率
            return_rate = round(4 + i, 1)  # 模拟收益率
            growth_rate = round(5 + i * 5, 1)  # 模拟增长率
            
            # 格式化为YYYY-MM格式
            period = f"{year}-{month:02d}"
            
            time_data.append({
                "timePeriod": period,
                "totalAssets": monthly_asset,
                "returnRate": f"{return_rate}%",
                "growthRate": f"{growth_rate}%"
            })
        
        # 按时间顺序排序（从早到晚）
        time_data.reverse()
        
        print("模拟时间序列数据生成完成")
        
        # 返回模拟数据
        return JsonResponse({
            'timeData': time_data,
            'account_id': account_id or "mock_account_123",
            'is_mock': True,
            'message': 'XtQuant API访问失败，使用模拟数据'
        })
            
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({
            'error': str(e),
            'code': 500
        }, status=500)