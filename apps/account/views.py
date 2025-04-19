import time
import datetime
import sys
import traceback
import os
from django.http import JsonResponse
from xtquant import xtdata
from xtquant.xttrader import XtQuantTrader, XtQuantTraderCallback
from xtquant.xttype import StockAccount
from rest_framework.decorators import api_view


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
def get_account_info(request):
    xt_trader = None
    try:
        # 创建交易接口实例
        path = r'D:\迅投极速交易终端 睿智融科版\userdata'
        
        # 检查路径是否存在
        if not os.path.exists(path):
            print(f"交易数据路径不存在: {path}")
            # 如果路径不存在，返回模拟账户数据
            account_list = [{
                'account_type': 'STOCK',
                'account_id': 'DEMO000001',
                'cash': 1000000,
                'frozen_cash': 50000,
                'market_value': 2000000,
                'total_asset': 3000000,
                'positions': [
                    {
                        'account_type': 'STOCK',
                        'account_id': 'DEMO000001',
                        'stock_code': '600000.SH',
                        'volume': 10000,
                        'can_use_volume': 10000,
                        'open_price': 12.5,
                        'market_value': 125000,
                        'frozen_volume': 0,
                        'on_road_volume': 0,
                        'yesterday_volume': 10000,
                        'avg_price': 11.8
                    }
                ]
            }]
            return JsonResponse({'accounts': account_list, 'error': '交易数据路径不存在'})
        
        # 使用当前时间戳作为session_id，确保唯一性
        session_id = int(time.time() * 1000)
        xt_trader = XtQuantTrader(path, session_id)
        callback = MyXtQuantTraderCallback()
        xt_trader.register_callback(callback)
        xt_trader.start()
        
        # 等待初始化完成
        time.sleep(1)

        # 建立交易连接，增加重试机制
        max_retries = 5  # 增加重试次数
        retry_count = 0
        connect_result = -1
        
        while retry_count < max_retries and connect_result != 0:
            print(f"正在尝试连接交易接口 - 第 {retry_count+1} 次尝试")
            connect_result = xt_trader.connect()
            if connect_result != 0:
                print(f"连接交易接口失败，错误码: {connect_result}，尝试第 {retry_count+1} 次重试")
                retry_count += 1
                time.sleep(2)  # 增加等待时间到2秒
        
        if connect_result != 0:
            print(f"连接交易接口失败，最终错误码: {connect_result}")
            # 连接失败，返回模拟账户数据
            account_list = [{
                'account_type': 'STOCK',
                'account_id': 'DEMO000001',
                'cash': 1000000,
                'frozen_cash': 50000,
                'market_value': 2000000,
                'total_asset': 3000000,
                'positions': [
                    {
                        'account_type': 'STOCK',
                        'account_id': 'DEMO000001',
                        'stock_code': '600000.SH',
                        'volume': 10000,
                        'can_use_volume': 10000,
                        'open_price': 12.5,
                        'market_value': 125000,
                        'frozen_volume': 0,
                        'on_road_volume': 0,
                        'yesterday_volume': 10000,
                        'avg_price': 11.8
                    }
                ]
            }]
            return JsonResponse({
                'accounts': account_list,
                'error': f'连接交易接口失败，错误码: {connect_result}'
            })
            
        # 连接成功后稍等片刻，确保系统初始化完成
        print("交易接口连接成功，等待系统初始化...")
        time.sleep(2)

        # 查询所有账户信息
        print("开始查询账户信息")
        accounts = xt_trader.query_account_infos()
        
        if not accounts:
            print("未查询到账户信息")
            account_list = [{
                'account_type': 'STOCK',
                'account_id': 'DEMO000001',
                'cash': 1000000,
                'frozen_cash': 50000,
                'market_value': 2000000,
                'total_asset': 3000000,
                'positions': []
            }]
            return JsonResponse({
                'accounts': account_list,
                'error': '未查询到账户信息'
            })
            
        print(f"查询到 {len(accounts)} 个账户")
        account_list = []
        
        for acc in accounts:
            print(f"处理账户: {acc.account_id}")
            # 订阅该账户的交易回调
            subscribe_result = xt_trader.subscribe(acc)
            print(f"订阅账户结果: {subscribe_result}")
            
            # 查询账户资产信息
            asset = xt_trader.query_stock_asset(acc)
            if asset is None:
                print(f"账户 {acc.account_id} 资产查询失败")
                continue
                
            print(f"账户 {acc.account_id} 资产查询成功")
            
            # 查询该账户的持仓信息
            positions = xt_trader.query_stock_positions(acc)
            pos_list = []
            
            if positions:
                print(f"账户 {acc.account_id} 持有 {len(positions)} 个持仓")
                for pos in positions:
                    pos_list.append({
                        'account_type': pos.account_type,  # 账号类型
                        'account_id': pos.account_id,  # 账号
                        'stock_code': pos.stock_code,  # 证券代码
                        'volume': pos.volume,  # 持仓数量
                        'can_use_volume': pos.can_use_volume,  # 可用数量
                        'open_price': pos.open_price,  # 开仓价
                        'market_value': pos.market_value,  # 市值
                        'frozen_volume': pos.frozen_volume,  # 冻结数量
                        'on_road_volume': pos.on_road_volume,  # 在途股份
                        'yesterday_volume': pos.yesterday_volume,  # 昨夜拥股
                        'avg_price': pos.avg_price,  # 成本价
                    })
            else:
                print(f"账户 {acc.account_id} 没有持仓")
                
            account_list.append({
                'account_type': asset.account_type,  # 账号类型
                'account_id': asset.account_id,  # 账号
                'cash': asset.cash,  # 可用金额
                'frozen_cash': asset.frozen_cash,  # 冻结金额
                'market_value': asset.market_value,  # 持仓市值
                'total_asset': asset.total_asset,  # 总资产
                'positions': pos_list,
            })

        print("完成账户信息查询")
        return JsonResponse({'accounts': account_list})
    except Exception as e:
        error_msg = f"获取账户信息异常: {str(e)}"
        print(error_msg)
        traceback.print_exc()
        # 发生异常，返回模拟账户数据
        account_list = [{
            'account_type': 'STOCK',
            'account_id': 'DEMO000001',
            'cash': 1000000,
            'frozen_cash': 50000,
            'market_value': 2000000,
            'total_asset': 3000000,
            'positions': [
                {
                    'account_type': 'STOCK',
                    'account_id': 'DEMO000001',
                    'stock_code': '600000.SH',
                    'volume': 10000,
                    'can_use_volume': 10000,
                    'open_price': 12.5,
                    'market_value': 125000,
                    'frozen_volume': 0,
                    'on_road_volume': 0,
                    'yesterday_volume': 10000,
                    'avg_price': 11.8
                }
            ]
        }]
        return JsonResponse({'accounts': account_list, 'error': error_msg})
    finally:
        # 确保资源释放
        if xt_trader:
            try:
                print("停止交易接口")
                xt_trader.stop()
            except Exception as e:
                print(f"停止交易接口时发生异常: {str(e)}")
