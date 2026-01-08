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


# ==================== 时间段对比模块 ====================

@api_view(['GET'])
def yearly_comparison(request):
    """
    年度对比接口
    API路径: /api/timecomparison/yearly_comparison/
    参数: account_id (必填)
    """
    logger.info('开始获取年度对比数据')
    
    # 检查是否使用模拟数据
    use_mock = request.GET.get('mock', 'true').lower() == 'true'
    account_id = request.GET.get('account_id')
    
    if not account_id:
        logger.error('缺少account_id参数')
        return JsonResponse({
            'success': False,
            'error': {
                'code': 'MISSING_PARAMETER',
                'message': '缺少account_id参数'
            }
        }, status=400)
    
    if use_mock:
        logger.info(f'使用模拟数据模式 - 账户ID: {account_id}')
        return get_mock_yearly_comparison()
    
    try:
        logger.info(f'开始获取账户 {account_id} 的年度对比数据（真实数据）')
        
        # 从数据库获取年度数据
        from apps.utils.data_storage import get_yearly_data
        
        yearly_data_dict = get_yearly_data(account_id)
        
        if not yearly_data_dict:
            logger.warning('未找到年度历史数据，返回模拟数据')
            return get_mock_yearly_comparison()
        
        # 转换为前端需要的格式
        yearly_data_list = []
        for year in sorted(yearly_data_dict.keys()):
            yearly_data_list.append({
                'year': year,
                'totalAssets': yearly_data_dict[year]['totalAssets'],
                'returnRate': yearly_data_dict[year]['returnRate'],
                'investmentRate': yearly_data_dict[year]['investmentRate']
            })
        
        logger.info(f'成功获取 {len(yearly_data_list)} 年的数据')
        return JsonResponse({
            'yearly_data': yearly_data_list
        })
        
    except Exception as e:
        logger.error(f'获取年度对比数据失败: {str(e)}', exc_info=True)
        logger.info('发生错误，返回模拟数据')
        return get_mock_yearly_comparison()


def get_mock_yearly_comparison():
    """
    返回年度对比模拟数据
    符合前端数据格式要求：使用year字段而不是timePeriod
    """
    logger.info('返回年度对比模拟数据')
    
    mock_data = {
        'yearly_data': [
            {
                'year': '2023',  # 前端要求使用year字段
                'totalAssets': 3200000.00,
                'returnRate': 12.50,  # 数字类型，不带%
                'investmentRate': 8.30
            },
            {
                'year': '2024',
                'totalAssets': 3680000.00,
                'returnRate': 15.00,
                'investmentRate': 9.50
            },
            {
                'year': '2025',
                'totalAssets': 4100000.00,
                'returnRate': 11.41,
                'investmentRate': 7.80
            }
        ]
    }
    
    return JsonResponse(mock_data)


@api_view(['GET'])
def weekly_comparison(request):
    """
    周度对比接口
    API路径: /api/timecomparison/weekly_comparison/
    参数: account_id (必填)
    """
    logger.info('开始获取周度对比数据')
    
    # 检查是否使用模拟数据
    use_mock = request.GET.get('mock', 'true').lower() == 'true'
    account_id = request.GET.get('account_id')
    
    if not account_id:
        logger.error('缺少account_id参数')
        return JsonResponse({
            'success': False,
            'error': {
                'code': 'MISSING_PARAMETER',
                'message': '缺少account_id参数'
            }
        }, status=400)
    
    if use_mock:
        logger.info(f'使用模拟数据模式 - 账户ID: {account_id}')
        return get_mock_weekly_comparison()
    
    try:
        logger.info(f'开始获取账户 {account_id} 的周度对比数据（真实数据）')
        
        # 从数据库获取周度数据
        from apps.utils.data_storage import get_weekly_data
        
        weekly_data_dict = get_weekly_data(account_id, weeks=4)
        
        if not weekly_data_dict:
            logger.warning('未找到周度历史数据，返回模拟数据')
            return get_mock_weekly_comparison()
        
        # 转换为前端需要的格式
        weekly_data_list = []
        for week_key in sorted(weekly_data_dict.keys()):
            weekly_data_list.append({
                'timePeriod': week_key,  # 前端要求使用timePeriod字段（周度）
                'totalAssets': weekly_data_dict[week_key]['totalAssets'],
                'returnRate': weekly_data_dict[week_key]['returnRate'],
                'investmentRate': weekly_data_dict[week_key]['investmentRate']
            })
        
        logger.info(f'成功获取 {len(weekly_data_list)} 周的数据')
        return JsonResponse({
            'weekly_data': weekly_data_list
        })
        
    except Exception as e:
        logger.error(f'获取周度对比数据失败: {str(e)}', exc_info=True)
        logger.info('发生错误，返回模拟数据')
        return get_mock_weekly_comparison()


def get_mock_weekly_comparison():
    """
    返回周度对比模拟数据
    周数格式: YYYY-WXX (ISO 8601标准)
    """
    logger.info('返回周度对比模拟数据')
    
    # 获取最近几周的周数
    from datetime import datetime, timedelta
    
    def get_iso_week(date):
        """获取ISO周数"""
        year, week, _ = date.isocalendar()
        return f"{year}-W{week:02d}"
    
    # 生成最近4周的数据
    current_date = datetime.now()
    weeks = []
    for i in range(4, 0, -1):
        week_date = current_date - timedelta(weeks=i-1)
        weeks.append(get_iso_week(week_date))
    
    mock_data = {
        'weekly_data': [
            {
                'timePeriod': weeks[0],
                'totalAssets': 3984000.00,
                'marketValue': 2772000.00,
                'returnRate': 6.2,  # 数字类型，不带%
                'growthRate': 9.8
            },
            {
                'timePeriod': weeks[1],
                'totalAssets': 4018000.00,
                'marketValue': 2793000.00,
                'returnRate': 6.5,
                'growthRate': 10.3
            },
            {
                'timePeriod': weeks[2],
                'totalAssets': 4055000.00,
                'marketValue': 2814000.00,
                'returnRate': 7.1,
                'growthRate': 11.2
            },
            {
                'timePeriod': weeks[3],
                'totalAssets': 4100000.00,
                'marketValue': 2850000.00,
                'returnRate': 8.0,
                'growthRate': 12.3
            }
        ],
        'current_total_assets': 4100000.00,
        'current_market_value': 2850000.00,
        'current_return_rate': 8.0,
        'is_mock': True
    }
    
    return JsonResponse(mock_data)


# ==================== 分市场对比模块 ====================

@api_view(['GET'])
def area_comparison(request):
    """
    地区对比接口
    API路径: /api/areacomparsion/area_comparison/
    参数: account_id (必填)
    
    ⚠️ 注意：这个接口的百分比必须是字符串格式并带%符号！
    """
    logger.info('开始获取地区对比数据')
    
    # 检查是否使用模拟数据
    use_mock = request.GET.get('mock', 'true').lower() == 'true'
    account_id = request.GET.get('account_id')
    
    if not account_id:
        logger.error('缺少account_id参数')
        return JsonResponse({
            'success': False,
            'error': {
                'code': 'MISSING_PARAMETER',
                'message': '缺少account_id参数'
            }
        }, status=400)
    
    if use_mock:
        logger.info(f'使用模拟数据模式 - 账户ID: {account_id}')
        return get_mock_area_comparison()
    
    try:
        logger.info(f'开始获取账户 {account_id} 的地区对比数据（真实数据）')
        
        # 使用统一的交易接口连接工具
        xt_trader, connected = get_xt_trader_connection()
        if not connected:
            logger.error('连接交易接口失败')
            logger.info('自动切换到模拟数据模式')
            return get_mock_area_comparison()

        # 查询账户信息
        acc = create_stock_account(account_id)
        xt_trader.subscribe(acc)

        # 查询账户资产信息
        asset = xt_trader.query_stock_asset(acc)
        if not asset:
            logger.error('未查询到账户资产信息')
            return get_mock_area_comparison()

        # 查询持仓信息
        positions = xt_trader.query_stock_positions(acc)
        if not positions:
            logger.warning('未查询到持仓信息')
            return get_mock_area_comparison()

        # 获取股票地区信息
        from apps.utils.stock_info import get_stock_region
        
        # 按地区汇总
        region_data_dict = {}
        total_assets = float(asset.total_asset)
        
        for pos in positions:
            stock_code = pos.stock_code
            market_value = float(pos.market_value)
            region = get_stock_region(stock_code)
            
            if region not in region_data_dict:
                region_data_dict[region] = {
                    'totalAssets': 0.0,
                    'market_values': []
                }
            
            region_data_dict[region]['totalAssets'] += market_value
            region_data_dict[region]['market_values'].append(market_value)
        
        # 计算回报率和投资占比
        # 注意：地区回报率需要从历史数据计算，这里简化处理
        region_data_list = []
        for region, data in region_data_dict.items():
            total_region_assets = data['totalAssets']
            investment_rate = (total_region_assets / total_assets * 100) if total_assets > 0 else 0
            
            # 计算回报率（简化：使用平均值，实际应该从历史数据计算）
            # 这里先使用一个估算值，实际应该从历史数据计算
            return_rate = 8.0  # TODO: 从历史数据计算真实回报率
            
            region_data_list.append({
                'region': region,
                'totalAssets': round(total_region_assets, 2),
                'returnRate': f'{return_rate:.1f}%',  # 字符串格式，带%符号
                'investmentRate': f'{investment_rate:.2f}%'  # 字符串格式，带%符号
            })
        
        # 按总资产降序排序
        region_data_list.sort(key=lambda x: x['totalAssets'], reverse=True)
        
        logger.info(f'成功获取 {len(region_data_list)} 个地区的数据')
        return JsonResponse({
            'region_data': region_data_list
        })
        
    except Exception as e:
        logger.error(f'获取地区对比数据失败: {str(e)}', exc_info=True)
        logger.info('发生错误，返回模拟数据')
        return get_mock_area_comparison()


def get_mock_area_comparison():
    """
    返回地区对比模拟数据
    ⚠️ 注意：returnRate 和 investmentRate 必须是字符串格式并带%符号
    """
    logger.info('返回地区对比模拟数据')
    
    mock_data = {
        'region_data': [
            {
                'region': '上海',
                'totalAssets': 820000.00,
                'returnRate': '8.5%',      # 字符串格式，带%符号
                'investmentRate': '28.8%'  # 字符串格式，带%符号
            },
            {
                'region': '深圳',
                'totalAssets': 712500.00,
                'returnRate': '7.8%',
                'investmentRate': '25.0%'
            },
            {
                'region': '北京',
                'totalAssets': 570000.00,
                'returnRate': '9.2%',
                'investmentRate': '20.0%'
            },
            {
                'region': '广州',
                'totalAssets': 342000.00,
                'returnRate': '6.5%',
                'investmentRate': '12.0%'
            },
            {
                'region': '杭州',
                'totalAssets': 228000.00,
                'returnRate': '7.0%',
                'investmentRate': '8.0%'
            },
            {
                'region': '其他',
                'totalAssets': 177500.00,
                'returnRate': '5.2%',
                'investmentRate': '6.2%'
            }
        ]
    }
    
    return JsonResponse(mock_data)


# ==================== 资产对比模块（优化版） ====================

@api_view(['GET'])
def asset_comparison(request):
    """
    资产对比接口（单个账户的资产占比分析）
    API路径: /api/asset_comparison/
    参数: account_id (必填)
    
    注意：这是原有的资产对比接口，用于单个账户内各股票的对比
    """
    logger.info('开始获取资产对比数据')
    
    # 检查是否使用模拟数据
    use_mock = request.GET.get('mock', 'true').lower() == 'true'
    account_id = request.GET.get('account_id')
    
    if not account_id:
        logger.error('缺少account_id参数')
        return JsonResponse({
            'success': False,
            'error': {
                'code': 'MISSING_PARAMETER',
                'message': '缺少account_id参数'
            }
        }, status=400)
    
    if use_mock:
        logger.info(f'使用模拟数据模式 - 账户ID: {account_id}')
        return get_mock_asset_comparison()
    
    try:
        logger.info(f'开始获取账户 {account_id} 的资产对比数据（真实数据）')
        
        # 使用统一的交易接口连接工具
        xt_trader, connected = get_xt_trader_connection()
        if not connected:
            logger.error('连接交易接口失败')
            logger.info('自动切换到模拟数据模式')
            return get_mock_asset_comparison()

        # 查询账户信息
        acc = create_stock_account(account_id)

        # 订阅该账户的交易回调
        subscribe_result = xt_trader.subscribe(acc)
        if subscribe_result != 0:
            logger.warning(f'订阅账户失败，错误码: {subscribe_result}')

        # 查询账户资产信息
        asset = xt_trader.query_stock_asset(acc)
        if not asset:
            logger.error('未查询到账户资产信息')
            return get_mock_asset_comparison()

        # 查询该账户的持仓信息
        positions = xt_trader.query_stock_positions(acc)
        if not positions:
            logger.warning('未查询到持仓信息')
            return JsonResponse({
                'total_market_value': 0.00,
                'positions': []
            })

        # 提取并计算用户持仓信息
        pos_list = []
        total_market_value = float(asset.market_value)  # 总持仓市值
        
        # 获取股票代码列表，用于查询股票名称
        stock_codes = [pos.stock_code for pos in positions]
        
        # 尝试从xtdata获取股票名称
        stock_names = {}
        try:
            for stock_code in stock_codes:
                try:
                    # 使用xtdata获取股票信息
                    instrument_detail = xtdata.get_instrument_detail(stock_code)
                    if instrument_detail and hasattr(instrument_detail, 'InstrumentName'):
                        stock_names[stock_code] = instrument_detail.InstrumentName
                    else:
                        # 如果获取失败，使用股票代码作为名称
                        stock_names[stock_code] = stock_code
                except Exception as e:
                    logger.warning(f'获取股票 {stock_code} 名称失败: {str(e)}')
                    stock_names[stock_code] = stock_code
        except Exception as e:
            logger.warning(f'批量获取股票名称失败: {str(e)}')
            # 如果批量获取失败，为每个股票代码设置默认名称
            for stock_code in stock_codes:
                stock_names[stock_code] = stock_code
        
        for pos in positions:
            stock_code = pos.stock_code  # 股票代码
            stock_name = stock_names.get(stock_code, stock_code)  # 股票名称
            market_value = float(pos.market_value)  # 市值
            avg_price = float(pos.avg_price)  # 成本价
            latest_price = float(pos.open_price)  # 最新价

            # 计算各支股票的资产占比
            asset_ratio = (market_value / total_market_value * 100) if total_market_value > 0 else 0

            # 计算当日涨幅（收益率）
            daily_return = ((latest_price - avg_price) / avg_price) * 100 if avg_price > 0 else 0

            pos_data = {
                'stock_code': stock_code,
                'stock_name': stock_name,
                'market_value': round(market_value, 2),
                'asset_ratio': round(asset_ratio, 2),
                'percentage': round(asset_ratio, 2),  # 兼容字段
                'daily_return': round(daily_return, 2),
                'profit_loss_rate': round(daily_return, 2)  # 兼容字段
            }
            pos_list.append(pos_data)

        # 按市值降序排序
        pos_list.sort(key=lambda x: x['market_value'], reverse=True)

        # 返回结果，同时支持asset_data和positions字段名（前端兼容）
        return JsonResponse({
            'total_market_value': round(total_market_value, 2),
            'asset_data': pos_list,  # 前端主要使用这个字段
            'positions': pos_list  # 兼容字段
        })

    except Exception as e:
        logger.error(f'获取资产对比数据失败: {str(e)}', exc_info=True)
        logger.info('发生错误，自动切换到模拟数据模式')
        return get_mock_asset_comparison()


def get_mock_asset_comparison():
    """
    返回资产对比模拟数据
    符合前端数据格式要求
    """
    logger.info('返回资产对比模拟数据')
    
    pos_list = [
        {
            'stock_code': '600519.SH',
            'stock_name': '贵州茅台',
            'market_value': 840250.00,
            'asset_ratio': 29.48,
            'percentage': 29.48,  # 兼容字段
            'daily_return': 15.08,
            'profit_loss_rate': 15.08  # 兼容字段
        },
        {
            'stock_code': '000858.SZ',
            'stock_name': '五粮液',
            'market_value': 466800.00,
            'asset_ratio': 16.38,
            'percentage': 16.38,
            'daily_return': 3.73,
            'profit_loss_rate': 3.73
        },
        {
            'stock_code': '601318.SH',
            'stock_name': '中国平安',
            'market_value': 637500.00,
            'asset_ratio': 22.37,
            'percentage': 22.37,
            'daily_return': 3.66,
            'profit_loss_rate': 3.66
        },
        {
            'stock_code': '600036.SH',
            'stock_name': '招商银行',
            'market_value': 716000.00,
            'asset_ratio': 25.09,
            'percentage': 25.09,
            'daily_return': 4.68,
            'profit_loss_rate': 4.68
        },
        {
            'stock_code': '000001.SZ',
            'stock_name': '平安银行',
            'market_value': 100000.00,
            'asset_ratio': 3.51,
            'percentage': 3.51,
            'daily_return': 5.93,
            'profit_loss_rate': 5.93
        }
    ]
    
    mock_data = {
        'total_market_value': 2850000.00,
        'asset_data': pos_list,  # 前端主要使用这个字段
        'positions': pos_list  # 兼容字段
    }
    
    return JsonResponse(mock_data)
