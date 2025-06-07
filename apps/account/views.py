import time
import datetime
import sys
import traceback
import os
from django.http import JsonResponse
from rest_framework.decorators import api_view
from xtquant import xtdata
from xtquant.xttrader import XtQuantTrader, XtQuantTraderCallback
from xtquant.xttype import StockAccount
from django.conf import settings

# 定义交易回调类
class MyXtQuantTraderCallback(XtQuantTraderCallback):
    def on_disconnected(self):
        """
        连接状态回调
        """
        print(datetime.datetime.now(), '连接断开回调')

    def on_stock_order(self, order):
        """
        委托信息推送
        :param order: XtOrder对象
        """
        print(datetime.datetime.now(), '委托回调 投资备注', order.order_remark)
        print(f"委托信息: 股票代码:{order.stock_code}, 委托状态:{order.order_status}, 系统编号:{order.order_sysid}")

    def on_stock_trade(self, trade):
        """
        成交信息推送
        :param trade: XtTrade对象
        """
        print(datetime.datetime.now(), '成交回调', trade.order_remark,
              f"委托方向(48买 49卖) {trade.offset_flag} 成交价格 {trade.traded_price} 成交数量 {trade.traded_volume}")
        print(f"成交信息: 账户ID:{trade.account_id}, 股票代码:{trade.stock_code}, 委托ID:{trade.order_id}")

    def on_order_error(self, order_error):
        """
        下单失败信息推送
        :param order_error: XtOrderError对象
        """
        print(f"委托报错回调 {order_error.order_remark} {order_error.error_msg}")
        print(f"下单失败: 委托ID:{order_error.order_id}, 错误ID:{order_error.error_id}, 错误信息:{order_error.error_msg}")

    def on_cancel_error(self, cancel_error):
        """
        撤单失败信息推送
        :param cancel_error: XtCancelError对象
        """
        print(datetime.datetime.now(), sys._getframe().f_code.co_name)
        print(f"撤单失败: 委托ID:{cancel_error.order_id}, 错误ID:{cancel_error.error_id}, 错误信息:{cancel_error.error_msg}")

    def on_order_stock_async_response(self, response):
        """
        异步下单回报推送
        :param response: XtOrderResponse对象
        """
        print(f"异步委托回调 投资备注: {response.order_remark}")
        print(f"异步下单回报: 账户ID:{response.account_id}, 委托ID:{response.order_id}, 序列号:{response.seq}")

    def on_cancel_order_stock_async_response(self, response):
        """
        异步撤单回报推送
        :param response: XtCancelOrderResponse对象
        """
        print(datetime.datetime.now(), sys._getframe().f_code.co_name)
        print(f"异步撤单回报: 账户ID:{response.account_id}, 委托ID:{response.order_id}, 序列号:{response.seq}")

    def on_account_status(self, status):
        """
        账号状态信息推送
        :param status: XtAccountStatus对象
        """
        print(datetime.datetime.now(), sys._getframe().f_code.co_name)
        print(f"账户状态: 账户ID:{status.account_id}, 账户类型:{status.account_type}, 状态:{status.status}")

@api_view(['GET'])
# API 视图：查询所有账户的资产及持仓数据
def get_account_info(request):
    # 获取账户ID参数（如果有）
    account_id = request.GET.get('account_id', None)
    
    xt_trader = None
    try:
        # 尝试从迅投获取真实数据
        print("尝试获取迅投API真实账户数据...")
        
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
            return JsonResponse({
                'error': '未找到有效的迅投数据目录，请检查迅投安装路径',
                'tried_paths': all_paths,
                'code': 404
            }, status=404)
            
        # 使用会话ID创建交易API实例
        session_id = int(time.time())
        print(f"使用迅投路径: {valid_path}, 会话ID: {session_id}")
        xt_trader = XtQuantTrader(valid_path, session_id)
        callback = MyXtQuantTraderCallback()
        xt_trader.register_callback(callback)
        
        # 准备API环境并启动API
        xt_trader.start()
        
        # 建立交易连接，返回 0 表示连接成功
        print("正在连接迅投交易接口...")
        connect_result = xt_trader.connect()
        if connect_result != 0:
            print(f"连接交易接口失败，错误码: {connect_result}")
            if connect_result == -1:
                error_msg = "登录失败，请检查迅投配置，确保迅投交易终端已登录"
            elif connect_result == -2:
                error_msg = "连接超时，请检查网络配置"
            else:
                error_msg = f"未知错误，错误码: {connect_result}"
                
            return JsonResponse({
                'error': error_msg,
                'code': connect_result,
                'xt_path': valid_path
            }, status=503)  # 服务不可用

        # 查询所有账户信息
        print("正在查询账户信息...")
        accounts = xt_trader.query_account_infos()
        if not accounts:
            print("未查询到账户信息，请确保已登录迅投并绑定了交易账户")
            return JsonResponse({
                'error': '未查询到账户信息，请确保已登录迅投并绑定了交易账户',
                'code': 404
            }, status=404)  # Not Found
            
        print(f"成功获取到 {len(accounts)} 个账户信息")
        account_list = []
        for acc in accounts:
            print(f"处理账户: {acc.account_id}, 类型: {acc.account_type}")
            
            # 如果指定了账户ID，则只处理该账户
            if account_id and acc.account_id != account_id:
                print(f"跳过非目标账户: {acc.account_id}")
                continue
                
            # 订阅该账户的交易回调
            subscribe_result = xt_trader.subscribe(acc)
            if subscribe_result != 0:
                print(f"订阅账户 {acc.account_id} 失败，错误码: {subscribe_result}")
                continue
                
            # 查询账户资产信息
            print(f"查询账户 {acc.account_id} 资产信息...")
            asset = xt_trader.query_stock_asset(acc)
            if asset is None:
                print(f"未获取到账户 {acc.account_id} 的资产信息")
                continue
                
            # 查询该账户的持仓信息
            print(f"查询账户 {acc.account_id} 持仓信息...")
            positions = xt_trader.query_stock_positions(acc)
            pos_list = []
            
            if positions:
                print(f"账户 {acc.account_id} 持有 {len(positions)} 个股票持仓")
                for pos in positions:
                    # 获取股票名称
                    stock_name = ""
                    try:
                        code_parts = pos.stock_code.split('.')
                        if len(code_parts) > 1:
                            base_code = code_parts[0]
                            market = code_parts[1]
                            # 通过XtData接口获取股票名称
                            stock_info = xtdata.get_stock_list_in_sector(f"A股{market}")
                            for stock in stock_info:
                                if stock.startswith(base_code):
                                    stock_name = xtdata.get_stock_name(stock)
                                    break
                    except Exception as e:
                        print(f"获取股票名称失败: {e}")
                    
                    # 根据文档中XtPosition结构添加必要字段
                    pos_list.append({
                        'account_type': pos.account_type,  # 账号类型
                        'account_id': pos.account_id,      # 账号
                        'stock_code': pos.stock_code,      # 证券代码
                        'stock_name': stock_name,          # 股票名称
                        'volume': pos.volume,              # 持仓数量
                        'can_use_volume': pos.can_use_volume,  # 可用数量
                        'open_price': pos.open_price,      # 开仓价
                        'market_value': pos.market_value,  # 市值
                        'frozen_volume': pos.frozen_volume,  # 冻结数量
                        'on_road_volume': pos.on_road_volume,  # 在途股份
                        'yesterday_volume': pos.yesterday_volume,  # 昨日持仓
                        'avg_price': pos.avg_price,        # 成本价
                        'update_time': int(time.time()),   # 更新时间戳
                        'market': pos.stock_code.split('.')[-1] if '.' in pos.stock_code else '',  # 交易市场
                    })
            else:
                print(f"账户 {acc.account_id} 没有持仓")
                    
            # 根据文档中XtAsset结构构建账户资产数据
            account_list.append({
                'account_type': asset.account_type,  # 账号类型
                'account_id': asset.account_id,      # 账号
                'cash': asset.cash,                  # 可用金额
                'frozen_cash': asset.frozen_cash,    # 冻结金额
                'market_value': asset.market_value,  # 持仓市值
                'total_asset': asset.total_asset,    # 总资产
                'fund_buy_amount': getattr(asset, 'fund_buy_amount', 0),  # 场内基金申购金额
                'fund_redeem_amount': getattr(asset, 'fund_redeem_amount', 0),  # 场内基金赎回金额
                'update_time': int(time.time()),  # 更新时间戳
                'positions': pos_list,
            })

        # 停止交易API
        if xt_trader:
            xt_trader.stop()
            print("已停止交易API")
        
        # 返回真实账户数据
        print(f"成功获取 {len(account_list)} 个账户的数据，返回结果...")
        return JsonResponse({'accounts': account_list})
        
    except Exception as e:
        print(f"处理账户资产数据时发生异常: {str(e)}")
        traceback.print_exc()
        # 尝试停止交易API（如果已初始化）
        try:
            if xt_trader:
                xt_trader.stop()
        except:
            pass
        
        # 返回错误信息
        return JsonResponse({
            'error': f'获取账户数据失败: {str(e)}',
            'code': 500
        }, status=500)

@api_view(['GET'])
def debug_params(request):
    """调试视图，显示所有接收到的参数"""
    get_params = dict(request.GET)
    post_params = dict(request.POST)
    headers = dict(request.headers)
    
    # 移除敏感信息
    if 'Authorization' in headers:
        headers['Authorization'] = 'REDACTED'
    
    # 尝试获取迅投配置信息（用于调试）
    xt_config = {}
    try:
        xt_config = {
            'USERDATA_PATH': settings.XT_CONFIG.get('USERDATA_PATH', '未配置'),
            'PATH_EXISTS': os.path.exists(settings.XT_CONFIG.get('USERDATA_PATH', '')),
            'API_KEY': '已配置' if settings.XT_CONFIG.get('API_KEY') else '未配置',
            'SECRET_KEY': '已配置' if settings.XT_CONFIG.get('SECRET_KEY') else '未配置',
            'TOKEN': '已配置' if settings.XT_CONFIG.get('TOKEN') else '未配置',
        }
    except Exception as e:
        xt_config = {'error': str(e)}
    
    return JsonResponse({
        'method': request.method,
        'path': request.path,
        'get_params': get_params,
        'post_params': post_params,
        'headers': headers,
        'xt_config': xt_config,
        'os_info': {
            'name': os.name,
            'current_dir': os.getcwd(),
        }
    })

@api_view(['GET'])
def debug_xtquant(request):
    """调试视图，显示XtQuant连接状态和详细配置信息"""
    import os
    import time
    from xtquant.xttrader import XtQuantTrader
    
    # 1. 检查XtQuant配置
    xt_config = {}
    try:
        xt_config = {
            'USERDATA_PATHS': settings.XT_CONFIG.get('USERDATA_PATHS', []),
            'USERDATA_PATH': settings.XT_CONFIG.get('USERDATA_PATH', '未配置'),
            'API_KEY': '已配置' if settings.XT_CONFIG.get('API_KEY') else '未配置',
            'SECRET_KEY': '已配置' if settings.XT_CONFIG.get('SECRET_KEY') else '未配置',
            'TOKEN': '已配置' if settings.XT_CONFIG.get('TOKEN') else '未配置',
        }
    except Exception as e:
        xt_config = {'error': str(e)}
    
    # 2. 检查路径
    path_checks = []
    all_paths = settings.XT_CONFIG.get('USERDATA_PATHS', [settings.XT_CONFIG.get('USERDATA_PATH')])
    valid_path = None
    
    for path in all_paths:
        exists = os.path.exists(path)
        path_checks.append({
            'path': path,
            'exists': exists,
            'readable': os.access(path, os.R_OK) if exists else False,
            'writable': os.access(path, os.W_OK) if exists else False,
        })
        
        if exists and not valid_path:
            valid_path = path
    
    # 3. 尝试连接XtQuant
    connection_test = {
        'success': False,
        'error': None,
        'details': {}
    }
    
    if valid_path:
        try:
            # 使用会话ID创建交易API实例
            session_id = int(time.time())
            print(f"使用迅投路径: {valid_path}, 会话ID: {session_id}")
            xt_trader = XtQuantTrader(valid_path, session_id)
            callback = MyXtQuantTraderCallback()
            xt_trader.register_callback(callback)
            
            # 准备API环境并启动API
            xt_trader.start()
            
            # 建立交易连接，返回 0 表示连接成功
            connect_result = xt_trader.connect()
            connection_test['details']['connect_result'] = connect_result
            
            if connect_result == 0:
                connection_test['success'] = True
                # 查询账户信息
                accounts = xt_trader.query_account_infos()
                connection_test['details']['accounts'] = [{'account_id': acc.account_id, 'account_type': acc.account_type} for acc in accounts] if accounts else []
            else:
                if connect_result == -1:
                    connection_test['error'] = "登录失败，请检查迅投配置，确保迅投交易终端已登录"
                elif connect_result == -2:
                    connection_test['error'] = "连接超时，请检查网络配置"
                else:
                    connection_test['error'] = f"未知错误，错误码: {connect_result}"
            
            # 停止交易API
            xt_trader.stop()
            
        except Exception as e:
            connection_test['error'] = str(e)
            connection_test['details']['exception_type'] = type(e).__name__
    else:
        connection_test['error'] = "未找到有效的迅投路径"
    
    # 4. 返回所有调试信息
    debug_info = {
        'xt_config': xt_config,
        'path_checks': path_checks,
        'valid_path': valid_path,
        'connection_test': connection_test,
        'os_info': {
            'name': os.name,
            'current_dir': os.getcwd(),
            'python_path': sys.executable,
        }
    }
    
    return JsonResponse(debug_info)

@api_view(['GET'])
def test_xtquant_environment(request):
    """测试迅投环境是否可用，尝试创建和读取文件"""
    import os
    import time
    import json
    from datetime import datetime
    
    results = {
        'success': False,
        'errors': [],
        'tests': [],
        'test_file_path': None
    }
    
    # 1. 查找有效的迅投路径
    valid_path = None
    all_paths = settings.XT_CONFIG.get('USERDATA_PATHS', [settings.XT_CONFIG.get('USERDATA_PATH')])
    
    for test_path in all_paths:
        if os.path.exists(test_path):
            valid_path = test_path
            results['tests'].append({
                'test': f"路径检查: {test_path}",
                'result': "成功"
            })
            break
        else:
            results['tests'].append({
                'test': f"路径检查: {test_path}",
                'result': "失败 - 路径不存在"
            })
    
    if not valid_path:
        results['errors'].append("未找到有效的迅投路径")
        return JsonResponse(results)
    
    # 2. 尝试在该路径中创建测试文件
    test_filename = f"xtquant_test_{int(time.time())}.json"
    test_file_path = os.path.join(valid_path, test_filename)
    results['test_file_path'] = test_file_path
    
    try:
        # 写入测试数据
        test_data = {
            'test_time': datetime.now().isoformat(),
            'app_name': 'StockVueVision',
            'test_note': 'This is a test file to verify XtQuant environment access',
        }
        
        with open(test_file_path, 'w') as f:
            json.dump(test_data, f)
        
        results['tests'].append({
            'test': f"文件写入: {test_file_path}",
            'result': "成功"
        })
        
        # 尝试读取刚刚写入的文件
        with open(test_file_path, 'r') as f:
            read_data = json.load(f)
        
        if read_data.get('test_time') == test_data.get('test_time'):
            results['tests'].append({
                'test': f"文件读取: {test_file_path}",
                'result': "成功"
            })
        else:
            results['tests'].append({
                'test': f"文件读取: {test_file_path}",
                'result': "失败 - 数据不匹配"
            })
            results['errors'].append("读取的数据与写入的数据不匹配")
        
        # 删除测试文件
        try:
            os.remove(test_file_path)
            results['tests'].append({
                'test': f"文件删除: {test_file_path}",
                'result': "成功"
            })
        except Exception as e:
            results['tests'].append({
                'test': f"文件删除: {test_file_path}",
                'result': f"失败 - {str(e)}"
            })
            results['errors'].append(f"无法删除测试文件: {str(e)}")
        
    except Exception as e:
        results['tests'].append({
            'test': f"文件操作: {test_file_path}",
            'result': f"失败 - {str(e)}"
        })
        results['errors'].append(f"文件操作失败: {str(e)}")
    
    # 3. 如果没有错误，标记为成功
    if not results['errors']:
        results['success'] = True
    
    # 4. 返回测试结果
    return JsonResponse(results)
