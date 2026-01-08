import time
import datetime
import logging
from django.http import JsonResponse
from rest_framework.decorators import api_view
from xtquant import xtdata
from django.conf import settings
from apps.utils.xt_trader import get_xt_trader_connection, create_stock_account

# 配置日志
logger = logging.getLogger(__name__)


@api_view(['GET'])
def get_account_info(request):
    """
    获取账户信息和持仓数据
    API文档: /api/account-info/
    支持模拟数据模式，通过查询参数 mock=true 启用
    """
    # 检查是否使用模拟数据
    use_mock = request.GET.get('mock', 'false').lower() == 'true'
    
    if use_mock:
        logger.info('使用模拟数据模式')
        return get_mock_account_info()
    
    try:
        logger.info('开始获取账户信息（真实数据）')
        
        # 使用统一的交易接口连接工具
        xt_trader, connected = get_xt_trader_connection()
        if not connected:
            logger.error('连接交易接口失败')
            logger.info('自动切换到模拟数据模式')
            return get_mock_account_info()

        # 查询所有账户信息
        accounts = xt_trader.query_account_infos()
        logger.info(f'查询到 {len(accounts)} 个账户')
        
        account_list = []
        for acc in accounts:
            try:
                # 订阅该账户的交易回调
                subscribe_result = xt_trader.subscribe(acc)
                
                # 查询账户资产信息
                asset = xt_trader.query_stock_asset(acc)
                if asset is None:
                    logger.warning(f'账户 {acc} 资产信息为空，跳过')
                    continue
                
                # 查询该账户的持仓信息
                positions = xt_trader.query_stock_positions(acc)
                
                # 转换持仓数据格式
                pos_list = convert_positions(positions, asset.account_id)
                
                # 构建账户数据 - 符合前端数据格式要求
                account_data = {
                    'account_id': str(asset.account_id),
                    'account_type': str(asset.account_type) if hasattr(asset, 'account_type') else 'STOCK',
                    'total_asset': float(asset.total_asset),  # 总资产（前端要求字段名）
                    'cash': float(asset.cash),  # 可用金额
                    'frozen_cash': float(asset.frozen_cash),  # 冻结金额
                    'market_value': float(asset.market_value),  # 持仓市值
                    'positions': pos_list
                }
                
                account_list.append(account_data)
                logger.info(f'成功处理账户 {asset.account_id}，持仓数量: {len(pos_list)}')
                
                # 自动保存账户快照到数据库（用于历史数据查询）
                try:
                    from apps.utils.data_storage import save_account_snapshot
                    save_account_snapshot(asset.account_id, account_data)
                except Exception as e:
                    logger.warning(f'保存账户快照失败: {str(e)}')
                    # 不影响主流程，只记录警告
                
            except Exception as e:
                logger.error(f'处理账户 {acc} 时出错: {str(e)}', exc_info=True)
                continue

        logger.info(f'成功返回 {len(account_list)} 个账户信息')
        return JsonResponse({'accounts': account_list})
        
    except Exception as e:
        logger.error(f'获取账户信息失败: {str(e)}', exc_info=True)
        logger.info('发生错误，自动切换到模拟数据模式')
        return get_mock_account_info()


def convert_positions(positions, account_id):
    """
    转换持仓数据为前端需要的格式
    - 数据类型转换（避免序列化错误）
    - 按市值降序排序
    - 返回前10条记录
    """
    if not positions:
        return []
    
    pos_list = []
    for pos in positions:
        try:
            # 确保所有数值类型正确转换
            pos_data = {
                'account_id': str(account_id),
                'account_type': str(pos.account_type) if hasattr(pos, 'account_type') else 'STOCK',
                'stock_code': str(pos.stock_code),  # 股票代码，如 "600000.SH"
                'stock_name': str(getattr(pos, 'stock_name', pos.stock_code)),  # 股票名称
                'volume': int(pos.volume),  # 持仓数量
                'can_use_volume': int(pos.can_use_volume),  # 可用数量
                'open_price': float(pos.open_price),  # 开仓价（当前价格）
                'market_value': float(pos.market_value),  # 市值
                'frozen_volume': int(pos.frozen_volume) if pos.frozen_volume else 0,  # 冻结数量
                'on_road_volume': int(pos.on_road_volume) if pos.on_road_volume else 0,  # 在途股份
                'yesterday_volume': int(pos.yesterday_volume),  # 昨日持仓
                'avg_price': float(pos.avg_price),  # 成本价
            }
            pos_list.append(pos_data)
        except Exception as e:
            logger.error(f'转换持仓数据失败 {pos.stock_code}: {str(e)}')
            continue
    
    # 按市值降序排序
    pos_list.sort(key=lambda x: x['market_value'], reverse=True)
    
    # 返回前10条（前端需求）
    return pos_list[:10]


def get_mock_account_info():
    """
    返回模拟账户数据
    用于测试和演示，当迅投连接不可用时自动使用
    """
    logger.info('返回模拟账户数据')
    
    mock_data = {
        'accounts': [
            {
                'account_id': 'DEMO000001',
                'account_type': 'STOCK',
                'cash': 1250000.00,
                'frozen_cash': 75000.00,
                'market_value': 2850000.00,
                'total_asset': 4100000.00,
                'positions': [
                    {
                        'account_id': 'DEMO000001',
                        'account_type': 'STOCK',
                        'stock_code': '600519.SH',
                        'stock_name': '贵州茅台',
                        'volume': 500,
                        'can_use_volume': 500,
                        'open_price': 1680.50,
                        'market_value': 840250.00,
                        'frozen_volume': 0,
                        'on_road_volume': 0,
                        'yesterday_volume': 500,
                        'avg_price': 1620.00
                    },
                    {
                        'account_id': 'DEMO000001',
                        'account_type': 'STOCK',
                        'stock_code': '600036.SH',
                        'stock_name': '招商银行',
                        'volume': 20000,
                        'can_use_volume': 20000,
                        'open_price': 35.80,
                        'market_value': 716000.00,
                        'frozen_volume': 0,
                        'on_road_volume': 0,
                        'yesterday_volume': 20000,
                        'avg_price': 34.20
                    },
                    {
                        'account_id': 'DEMO000001',
                        'account_type': 'STOCK',
                        'stock_code': '601318.SH',
                        'stock_name': '中国平安',
                        'volume': 15000,
                        'can_use_volume': 15000,
                        'open_price': 42.50,
                        'market_value': 637500.00,
                        'frozen_volume': 0,
                        'on_road_volume': 0,
                        'yesterday_volume': 15000,
                        'avg_price': 41.00
                    },
                    {
                        'account_id': 'DEMO000001',
                        'account_type': 'STOCK',
                        'stock_code': '000858.SZ',
                        'stock_name': '五粮液',
                        'volume': 3000,
                        'can_use_volume': 3000,
                        'open_price': 155.60,
                        'market_value': 466800.00,
                        'frozen_volume': 0,
                        'on_road_volume': 0,
                        'yesterday_volume': 3000,
                        'avg_price': 150.00
                    },
                    {
                        'account_id': 'DEMO000001',
                        'account_type': 'STOCK',
                        'stock_code': '000001.SZ',
                        'stock_name': '平安银行',
                        'volume': 8000,
                        'can_use_volume': 8000,
                        'open_price': 12.50,
                        'market_value': 100000.00,
                        'frozen_volume': 0,
                        'on_road_volume': 0,
                        'yesterday_volume': 8000,
                        'avg_price': 11.80
                    },
                    {
                        'account_id': 'DEMO000001',
                        'account_type': 'STOCK',
                        'stock_code': '600887.SH',
                        'stock_name': '伊利股份',
                        'volume': 2500,
                        'can_use_volume': 2500,
                        'open_price': 28.90,
                        'market_value': 72250.00,
                        'frozen_volume': 0,
                        'on_road_volume': 0,
                        'yesterday_volume': 2500,
                        'avg_price': 27.50
                    },
                    {
                        'account_id': 'DEMO000001',
                        'account_type': 'STOCK',
                        'stock_code': '601012.SH',
                        'stock_name': '隆基绿能',
                        'volume': 1200,
                        'can_use_volume': 1200,
                        'open_price': 18.30,
                        'market_value': 21960.00,
                        'frozen_volume': 0,
                        'on_road_volume': 0,
                        'yesterday_volume': 1200,
                        'avg_price': 20.00
                    },
                    {
                        'account_id': 'DEMO000001',
                        'account_type': 'STOCK',
                        'stock_code': '300750.SZ',
                        'stock_name': '宁德时代',
                        'volume': 100,
                        'can_use_volume': 100,
                        'open_price': 165.80,
                        'market_value': 16580.00,
                        'frozen_volume': 0,
                        'on_road_volume': 0,
                        'yesterday_volume': 100,
                        'avg_price': 180.00
                    }
                ]
            }
        ]
    }
    
    return JsonResponse(mock_data)


@api_view(['GET'])
def get_asset_category(request):
    """
    获取资产分类数据
    API文档: /api/asset-category/
    根据股票所属行业/板块进行分类统计
    符合前端数据格式要求：使用categories字段，category和totalAssets字段名
    """
    logger.info('获取资产分类数据')
    
    # 检查是否使用模拟数据
    use_mock = request.GET.get('mock', 'true').lower() == 'true'
    
    if use_mock:
        # 模拟数据 - 符合前端格式要求
        category_data = {
            'categories': [  # 前端要求使用categories字段
                {
                    'category': '股票',  # 前端要求使用category字段
                    'totalAssets': 2850000.00,  # 前端要求使用totalAssets字段
                    'percentage': 69.51
                },
                {
                    'category': '现金',
                    'totalAssets': 1250000.00,
                    'percentage': 30.49
                }
            ]
        }
        return JsonResponse(category_data)
    
    try:
        logger.info('开始获取资产分类数据（真实数据）')
        
        # 使用统一的交易接口连接工具
        xt_trader, connected = get_xt_trader_connection()
        if not connected:
            logger.error('连接交易接口失败')
            logger.info('自动切换到模拟数据模式')
            return JsonResponse({
                'categories': [
                    {'category': '股票', 'totalAssets': 2850000.00, 'percentage': 69.51},
                    {'category': '现金', 'totalAssets': 1250000.00, 'percentage': 30.49}
                ]
            })

        # 查询所有账户信息
        accounts = xt_trader.query_account_infos()
        if not accounts:
            logger.warning('未查询到账户信息')
            return JsonResponse({
                'categories': [
                    {'category': '股票', 'totalAssets': 0.00, 'percentage': 0.00},
                    {'category': '现金', 'totalAssets': 0.00, 'percentage': 0.00}
                ]
            })

        # 汇总所有账户的数据
        total_market_value = 0.0
        total_cash = 0.0
        
        for acc in accounts:
            try:
                xt_trader.subscribe(acc)
                asset = xt_trader.query_stock_asset(acc)
                if asset:
                    total_market_value += float(asset.market_value)
                    total_cash += float(asset.cash)
            except Exception as e:
                logger.warning(f'处理账户 {acc} 时出错: {str(e)}')
                continue
        
        total_assets = total_market_value + total_cash
        
        # 计算占比
        stock_percentage = (total_market_value / total_assets * 100) if total_assets > 0 else 0
        cash_percentage = (total_cash / total_assets * 100) if total_assets > 0 else 0
        
        logger.info(f'成功获取资产分类数据：股票 {total_market_value:.2f}，现金 {total_cash:.2f}')
        return JsonResponse({
            'categories': [
                {
                    'category': '股票',
                    'totalAssets': round(total_market_value, 2),
                    'percentage': round(stock_percentage, 2)
                },
                {
                    'category': '现金',
                    'totalAssets': round(total_cash, 2),
                    'percentage': round(cash_percentage, 2)
                }
            ]
        })
        
    except Exception as e:
        logger.error(f'获取资产分类数据失败: {str(e)}', exc_info=True)
        # 发生错误时返回模拟数据
        return JsonResponse({
            'categories': [
                {'category': '股票', 'totalAssets': 2850000.00, 'percentage': 69.51},
                {'category': '现金', 'totalAssets': 1250000.00, 'percentage': 30.49}
            ]
        })


@api_view(['GET'])
def get_region_data(request):
    """
    获取地区分布数据
    API文档: /api/region-data/
    根据股票上市地区进行统计
    符合前端数据格式要求：使用regions字段，region和totalAssets字段名
    """
    logger.info('获取地区分布数据')
    
    # 检查是否使用模拟数据
    use_mock = request.GET.get('mock', 'true').lower() == 'true'
    
    if use_mock:
        # 模拟数据 - 符合前端格式要求
        region_data = {
            'regions': [  # 前端要求使用regions字段
                {
                    'region': '上海',  # 前端要求使用region字段
                    'totalAssets': 1353500.00,  # 前端要求使用totalAssets字段
                    'percentage': 28.77
                },
                {
                    'region': '深圳',
                    'totalAssets': 712500.00,
                    'percentage': 25.00
                },
                {
                    'region': '北京',
                    'totalAssets': 570000.00,
                    'percentage': 20.00
                },
                {
                    'region': '广州',
                    'totalAssets': 342000.00,
                    'percentage': 12.00
                },
                {
                    'region': '杭州',
                    'totalAssets': 228000.00,
                    'percentage': 8.00
                },
                {
                    'region': '其他',
                    'totalAssets': 177500.00,
                    'percentage': 6.23
                }
            ]
        }
        return JsonResponse(region_data)
    
    try:
        logger.info('开始获取地区分布数据（真实数据）')
        
        # 使用统一的交易接口连接工具
        xt_trader, connected = get_xt_trader_connection()
        if not connected:
            logger.error('连接交易接口失败')
            logger.info('自动切换到模拟数据模式')
            return JsonResponse({
                'regions': [
                    {'region': '上海', 'totalAssets': 1353500.00, 'percentage': 28.77}
                ]
            })

        # 查询所有账户信息
        accounts = xt_trader.query_account_infos()
        if not accounts:
            logger.warning('未查询到账户信息')
            return JsonResponse({'regions': []})

        # 获取股票地区信息
        from apps.utils.stock_info import get_stock_region
        
        # 按地区汇总
        region_data_dict = {}
        total_market_value = 0.0
        
        for acc in accounts:
            try:
                xt_trader.subscribe(acc)
                positions = xt_trader.query_stock_positions(acc)
                if positions:
                    for pos in positions:
                        stock_code = pos.stock_code
                        market_value = float(pos.market_value)
                        region = get_stock_region(stock_code)
                        
                        if region not in region_data_dict:
                            region_data_dict[region] = 0.0
                        
                        region_data_dict[region] += market_value
                        total_market_value += market_value
            except Exception as e:
                logger.warning(f'处理账户 {acc} 时出错: {str(e)}')
                continue
        
        # 计算占比并转换为列表
        region_list = []
        for region, assets in region_data_dict.items():
            percentage = (assets / total_market_value * 100) if total_market_value > 0 else 0
            region_list.append({
                'region': region,
                'totalAssets': round(assets, 2),
                'percentage': round(percentage, 2)
            })
        
        # 按总资产降序排序
        region_list.sort(key=lambda x: x['totalAssets'], reverse=True)
        
        logger.info(f'成功获取 {len(region_list)} 个地区的数据')
        return JsonResponse({
            'regions': region_list
        })
        
    except Exception as e:
        logger.error(f'获取地区分布数据失败: {str(e)}', exc_info=True)
        # 发生错误时返回模拟数据
        return JsonResponse({
            'regions': [
                {'region': '上海', 'totalAssets': 1353500.00, 'percentage': 28.77}
            ]
        })


@api_view(['GET'])
def get_time_data(request):
    """
    获取时间序列数据
    API文档: /api/time-data/
    符合前端数据格式要求：返回时间序列数据
    """
    logger.info('获取时间序列数据')
    
    # 获取参数
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    use_mock = request.GET.get('mock', 'true').lower() == 'true'
    
    if use_mock:
        # 模拟数据 - 符合前端格式要求
        import random
        from datetime import timedelta
        
        # 如果没有指定日期，默认返回最近30天
        if not end_date:
            end_date = datetime.datetime.now().strftime('%Y-%m-%d')
        if not start_date:
            start_date = (datetime.datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        # 生成时间序列数据
        time_series = []
        current_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.datetime.strptime(end_date, '%Y-%m-%d')
        base_value = 3800000.00
        
        while current_date <= end_dt:
            # 添加随机波动
            daily_change = random.uniform(-0.02, 0.02)  # -2% 到 +2%
            base_value = base_value * (1 + daily_change)
            
            # 计算回报率（简化计算）
            return_rate = (base_value - 3800000.00) / 3800000.00 * 100
            
            time_series.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'totalAssets': round(base_value, 2),
                'returnRate': round(return_rate, 2)
            })
            
            current_date += timedelta(days=1)
        
        return JsonResponse({
            'time_series': time_series
        })
    
    try:
        logger.info('开始获取时间序列数据（真实数据）')
        
        # 获取第一个账户ID（如果前端需要指定账户，可以添加account_id参数）
        # 这里暂时使用数据库中的第一个账户
        from apps.utils.data_storage import get_account_history
        from apps.utils.db import get_mongodb_db
        
        # 如果没有指定账户，尝试从数据库获取最新的账户
        db = get_mongodb_db()
        
        # 获取最新的账户快照，提取account_id
        latest_snapshot = db.account_snapshots.find_one(sort=[('timestamp', -1)])
        if not latest_snapshot:
            logger.warning('未找到历史数据，返回模拟数据')
            return JsonResponse({
                'time_series': [
                    {
                        'date': datetime.datetime.now().strftime('%Y-%m-%d'),
                        'totalAssets': 4100000.00,
                        'returnRate': 8.0
                    }
                ]
            })
        
        account_id = latest_snapshot.get('account_id')
        
        # 获取历史数据
        history = get_account_history(account_id, start_date=start_date, end_date=end_date, days=30)
        
        if not history:
            logger.warning('未找到历史数据，返回模拟数据')
            return JsonResponse({
                'time_series': [
                    {
                        'date': datetime.datetime.now().strftime('%Y-%m-%d'),
                        'totalAssets': 4100000.00,
                        'returnRate': 8.0
                    }
                ]
            })
        
        # 计算回报率（相对于第一天的资产）
        if len(history) > 0:
            initial_assets = history[0]['total_assets']
        else:
            initial_assets = 0
        
        time_series = []
        for record in history:
            current_assets = record['total_assets']
            return_rate = ((current_assets - initial_assets) / initial_assets * 100) if initial_assets > 0 else 0
            
            time_series.append({
                'date': record['date'],
                'totalAssets': round(current_assets, 2),
                'returnRate': round(return_rate, 2)
            })
        
        logger.info(f'成功获取 {len(time_series)} 条时间序列数据')
        return JsonResponse({
            'time_series': time_series
        })
        
    except Exception as e:
        logger.error(f'获取时间序列数据失败: {str(e)}', exc_info=True)
        # 发生错误时返回模拟数据
        return JsonResponse({
            'time_series': [
                {
                    'date': datetime.datetime.now().strftime('%Y-%m-%d'),
                    'totalAssets': 4100000.00,
                    'returnRate': 8.0
                }
            ]
        })
