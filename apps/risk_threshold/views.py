"""
风险阈值模块 - 视图函数
包含四个主要风险指标的计算和API：
1. 最大本金损失
2. 波动率
3. 最大回撤
4. VaR值（风险价值）
"""

import logging
import numpy as np
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.conf import settings
from rest_framework.decorators import api_view

# 配置日志
logger = logging.getLogger(__name__)


# ==================== 辅助函数：从迅投获取历史数据 ====================

def get_account_history_from_xt(account_id, days=30):
    """
    从迅投API获取账户历史数据
    
    参数:
        account_id: 账户ID
        days: 获取最近多少天的数据
    
    返回:
        list: 每日资产数据列表
        [
            {
                'date': '2025-01-01',
                'total_assets': 4100000.00,
                'market_value': 2850000.00,
                'cash': 1250000.00
            },
            ...
        ]
    """
    try:
        # 从数据库获取账户历史数据
        from apps.utils.data_storage import get_account_history
        
        logger.info(f'从数据库获取账户 {account_id} 最近 {days} 天的历史数据')
        
        history = get_account_history(account_id, days=days)
        
        if not history:
            logger.warning(f'未找到账户 {account_id} 的历史数据')
            return None
        
        logger.info(f'成功获取 {len(history)} 条历史数据')
        return history
        
    except Exception as e:
        logger.error(f'从数据库获取历史数据失败: {str(e)}', exc_info=True)
        return None


def get_position_history_from_xt(account_id, days=30):
    """
    从迅投API获取持仓历史数据
    
    参数:
        account_id: 账户ID
        days: 获取最近多少天的数据
    
    返回:
        list: 持仓历史数据
    """
    try:
        from xtquant import xtdata
        
        # TODO: 调用迅投API获取持仓历史记录
        logger.info(f'从迅投获取账户 {account_id} 持仓历史数据')
        
        return None
        
    except Exception as e:
        logger.error(f'从迅投获取持仓历史失败: {str(e)}')
        return None


# ==================== 风险指标计算函数 ====================

def calculate_max_principal_loss(account_history):
    """
    计算最大本金损失
    
    公式: (初始资金 - 当前资金) / 初始资金 × 100%
    
    参数:
        account_history: 账户历史数据列表
    
    返回:
        dict: {
            'max_loss_amount': 最大损失金额,
            'max_loss_rate': 最大损失率(%),
            'initial_capital': 初始资金,
            'current_capital': 当前资金
        }
    """
    if not account_history or len(account_history) == 0:
        return None
    
    initial_capital = account_history[0]['total_assets']
    current_capital = account_history[-1]['total_assets']
    
    loss_amount = initial_capital - current_capital
    loss_rate = (loss_amount / initial_capital * 100) if initial_capital > 0 else 0
    
    return {
        'max_loss_amount': round(loss_amount, 2),
        'max_loss_rate': round(loss_rate, 2),
        'initial_capital': round(initial_capital, 2),
        'current_capital': round(current_capital, 2)
    }


def calculate_volatility(account_history):
    """
    计算波动率（使用日收益率的标准差）
    
    参数:
        account_history: 账户历史数据列表
    
    返回:
        dict: {
            'daily_volatility': 日波动率(%),
            'annual_volatility': 年化波动率(%),
            'volatility_level': 波动性等级
        }
    """
    if not account_history or len(account_history) < 2:
        return None
    
    # 计算日收益率
    daily_returns = []
    for i in range(1, len(account_history)):
        prev_value = account_history[i-1]['total_assets']
        curr_value = account_history[i]['total_assets']
        if prev_value > 0:
            daily_return = (curr_value - prev_value) / prev_value
            daily_returns.append(daily_return)
    
    if len(daily_returns) == 0:
        return None
    
    # 计算标准差（波动率）
    daily_volatility = np.std(daily_returns) * 100  # 转换为百分比
    annual_volatility = daily_volatility * np.sqrt(252)  # 年化波动率（假设252个交易日）
    
    # 判断波动性等级
    if annual_volatility < 10:
        volatility_level = '低'
    elif annual_volatility < 20:
        volatility_level = '中'
    else:
        volatility_level = '高'
    
    return {
        'daily_volatility': round(daily_volatility, 2),
        'annual_volatility': round(annual_volatility, 2),
        'volatility_level': volatility_level
    }


def calculate_max_drawdown(account_history):
    """
    计算最大回撤
    
    公式: (资产最高点 - 最高点之后的最低点) / 资产最高点 × 100%
    
    参数:
        account_history: 账户历史数据列表
    
    返回:
        dict: {
            'max_drawdown': 最大回撤率(%),
            'max_drawdown_amount': 最大回撤金额,
            'peak_value': 峰值资产,
            'peak_date': 峰值日期,
            'valley_value': 谷底资产,
            'valley_date': 谷底日期
        }
    """
    if not account_history or len(account_history) < 2:
        return None
    
    max_drawdown = 0
    max_drawdown_amount = 0
    peak_value = account_history[0]['total_assets']
    peak_date = account_history[0]['date']
    valley_value = peak_value
    valley_date = peak_date
    current_peak = peak_value
    current_peak_date = peak_date
    
    for record in account_history:
        current_value = record['total_assets']
        current_date = record['date']
        
        # 更新当前峰值
        if current_value > current_peak:
            current_peak = current_value
            current_peak_date = current_date
        
        # 计算回撤
        drawdown = (current_peak - current_value) / current_peak if current_peak > 0 else 0
        
        # 更新最大回撤
        if drawdown > max_drawdown:
            max_drawdown = drawdown
            max_drawdown_amount = current_peak - current_value
            peak_value = current_peak
            peak_date = current_peak_date
            valley_value = current_value
            valley_date = current_date
    
    return {
        'max_drawdown': round(max_drawdown * 100, 2),  # 转换为百分比
        'max_drawdown_amount': round(max_drawdown_amount, 2),
        'peak_value': round(peak_value, 2),
        'peak_date': peak_date,
        'valley_value': round(valley_value, 2),
        'valley_date': valley_date
    }


def calculate_var(account_history, confidence_level=0.95):
    """
    计算VaR值（Value at Risk - 风险价值）
    
    使用历史模拟法计算在指定置信水平下的最大可能损失
    
    参数:
        account_history: 账户历史数据列表
        confidence_level: 置信水平，默认95%
    
    返回:
        dict: {
            'var_amount': VaR金额,
            'var_rate': VaR比率(%),
            'confidence_level': 置信水平,
            'current_value': 当前资产价值
        }
    """
    if not account_history or len(account_history) < 2:
        return None
    
    # 计算日收益率
    daily_returns = []
    for i in range(1, len(account_history)):
        prev_value = account_history[i-1]['total_assets']
        curr_value = account_history[i]['total_assets']
        if prev_value > 0:
            daily_return = (curr_value - prev_value) / prev_value
            daily_returns.append(daily_return)
    
    if len(daily_returns) == 0:
        return None
    
    # 计算VaR（历史模拟法）
    current_value = account_history[-1]['total_assets']
    var_percentile = np.percentile(daily_returns, (1 - confidence_level) * 100)
    var_amount = abs(current_value * var_percentile)
    var_rate = abs(var_percentile * 100)
    
    return {
        'var_amount': round(var_amount, 2),
        'var_rate': round(var_rate, 2),
        'confidence_level': confidence_level * 100,
        'current_value': round(current_value, 2)
    }


# ==================== 模拟数据生成函数 ====================

def get_mock_account_history(days=30):
    """
    生成模拟的账户历史数据
    
    参数:
        days: 生成多少天的数据
    
    返回:
        list: 模拟的账户历史数据
    """
    logger.info(f'生成 {days} 天的模拟账户历史数据')
    
    # 设置随机种子以获得可复现的结果
    np.random.seed(42)
    
    base_value = 4100000.00  # 初始资产
    current_date = datetime.now()
    
    history = []
    current_value = base_value
    
    for i in range(days, 0, -1):
        date = (current_date - timedelta(days=i)).strftime('%Y-%m-%d')
        
        # 添加随机波动（日收益率在-2%到+2%之间）
        daily_return = np.random.normal(0.001, 0.015)  # 均值0.1%，标准差1.5%
        current_value = current_value * (1 + daily_return)
        
        # 确保不会变成负数
        current_value = max(current_value, base_value * 0.7)
        
        history.append({
            'date': date,
            'total_assets': round(current_value, 2),
            'market_value': round(current_value * 0.7, 2),
            'cash': round(current_value * 0.3, 2)
        })
    
    return history


def get_risk_level(max_loss_rate, volatility, max_drawdown, var_rate):
    """
    根据各项风险指标综合判断风险等级
    
    参数:
        max_loss_rate: 最大本金损失率(%)
        volatility: 年化波动率(%)
        max_drawdown: 最大回撤(%)
        var_rate: VaR比率(%)
    
    返回:
        str: 风险等级 ('低', '中', '高')
    """
    # 计算风险分数（0-100）
    risk_score = 0
    
    # 最大本金损失占25分
    if max_loss_rate > 20:
        risk_score += 25
    elif max_loss_rate > 10:
        risk_score += 15
    elif max_loss_rate > 5:
        risk_score += 5
    
    # 波动率占25分
    if volatility > 30:
        risk_score += 25
    elif volatility > 20:
        risk_score += 15
    elif volatility > 10:
        risk_score += 5
    
    # 最大回撤占25分
    if max_drawdown > 30:
        risk_score += 25
    elif max_drawdown > 20:
        risk_score += 15
    elif max_drawdown > 10:
        risk_score += 5
    
    # VaR占25分
    if var_rate > 5:
        risk_score += 25
    elif var_rate > 3:
        risk_score += 15
    elif var_rate > 2:
        risk_score += 5
    
    # 根据总分判断等级
    if risk_score >= 60:
        return '高'
    elif risk_score >= 30:
        return '中'
    else:
        return '低'


# ==================== API视图函数 ====================

@api_view(['GET'])
def get_risk_assessment(request):
    """
    综合风险评估接口
    返回所有风险指标和综合评级
    
    API路径: /api/risk-threshold/assessment/
    参数: account_id (必填), days (可选，默认30天), mock (可选，默认true)
    
    返回数据示例:
    {
        "account_id": "DEMO000001",
        "assessment_date": "2025-01-15",
        "period_days": 30,
        "max_principal_loss": {
            "max_loss_amount": 50000.00,
            "max_loss_rate": 1.22,
            "initial_capital": 4100000.00,
            "current_capital": 4050000.00,
            "status": "正常"
        },
        "volatility": {
            "daily_volatility": 1.45,
            "annual_volatility": 23.02,
            "volatility_level": "中",
            "status": "正常"
        },
        "max_drawdown": {
            "max_drawdown": 5.25,
            "max_drawdown_amount": 215250.00,
            "peak_value": 4100000.00,
            "peak_date": "2025-01-01",
            "valley_value": 3884750.00,
            "valley_date": "2025-01-10",
            "status": "正常"
        },
        "var": {
            "var_amount": 61500.00,
            "var_rate": 1.50,
            "confidence_level": 95,
            "current_value": 4100000.00,
            "status": "正常"
        },
        "overall_risk": {
            "risk_level": "中",
            "risk_score": 35,
            "recommendation": "当前风险处于中等水平，建议关注市场波动"
        },
        "is_mock": true
    }
    """
    logger.info('收到风险评估请求')
    
    # 获取参数
    account_id = request.GET.get('account_id')
    days = int(request.GET.get('days', 30))
    use_mock = request.GET.get('mock', 'true').lower() == 'true'
    
    if not account_id:
        logger.error('缺少account_id参数')
        return JsonResponse({
            'success': False,
            'error': {
                'code': 'MISSING_PARAMETER',
                'message': '缺少account_id参数'
            }
        }, status=400)
    
    # 获取历史数据
    if not use_mock:
        account_history = get_account_history_from_xt(account_id, days)
    else:
        account_history = None
    
    # 如果没有真实数据，使用模拟数据
    if account_history is None:
        logger.info('使用模拟数据')
        account_history = get_mock_account_history(days)
        is_mock = True
    else:
        is_mock = False
    
    # 计算各项风险指标
    max_loss = calculate_max_principal_loss(account_history)
    volatility = calculate_volatility(account_history)
    max_dd = calculate_max_drawdown(account_history)
    var = calculate_var(account_history, confidence_level=0.95)
    
    # 判断各指标状态
    max_loss_status = '正常' if abs(max_loss['max_loss_rate']) < 10 else '警告' if abs(max_loss['max_loss_rate']) < 20 else '危险'
    volatility_status = '正常' if volatility['annual_volatility'] < 20 else '警告' if volatility['annual_volatility'] < 30 else '危险'
    max_dd_status = '正常' if max_dd['max_drawdown'] < 15 else '警告' if max_dd['max_drawdown'] < 25 else '危险'
    var_status = '正常' if var['var_rate'] < 3 else '警告' if var['var_rate'] < 5 else '危险'
    
    # 综合风险评估
    risk_level = get_risk_level(
        abs(max_loss['max_loss_rate']),
        volatility['annual_volatility'],
        max_dd['max_drawdown'],
        var['var_rate']
    )
    
    # 生成建议
    if risk_level == '低':
        recommendation = '当前风险较低，可以适当增加投资'
    elif risk_level == '中':
        recommendation = '当前风险处于中等水平，建议关注市场波动'
    else:
        recommendation = '当前风险较高，建议降低仓位或采取对冲措施'
    
    # 构建返回数据
    response_data = {
        'account_id': account_id,
        'assessment_date': datetime.now().strftime('%Y-%m-%d'),
        'period_days': days,
        'max_principal_loss': {
            **max_loss,
            'status': max_loss_status
        },
        'volatility': {
            **volatility,
            'status': volatility_status
        },
        'max_drawdown': {
            **max_dd,
            'status': max_dd_status
        },
        'var': {
            **var,
            'status': var_status
        },
        'overall_risk': {
            'risk_level': risk_level,
            'recommendation': recommendation
        },
        'is_mock': is_mock
    }
    
    logger.info(f'风险评估完成: {risk_level}')
    return JsonResponse(response_data)


@api_view(['GET'])
def get_max_principal_loss(request):
    """
    最大本金损失接口
    API路径: /api/risk-threshold/max-principal-loss/
    """
    account_id = request.GET.get('account_id')
    days = int(request.GET.get('days', 30))
    use_mock = request.GET.get('mock', 'true').lower() == 'true'
    
    if not account_id:
        return JsonResponse({'success': False, 'error': '缺少account_id参数'}, status=400)
    
    account_history = get_mock_account_history(days) if use_mock else get_account_history_from_xt(account_id, days)
    
    if account_history is None:
        account_history = get_mock_account_history(days)
    
    result = calculate_max_principal_loss(account_history)
    result['is_mock'] = use_mock
    
    return JsonResponse(result)


@api_view(['GET'])
def get_volatility(request):
    """
    波动率接口
    API路径: /api/risk-threshold/volatility/
    """
    account_id = request.GET.get('account_id')
    days = int(request.GET.get('days', 30))
    use_mock = request.GET.get('mock', 'true').lower() == 'true'
    
    if not account_id:
        return JsonResponse({'success': False, 'error': '缺少account_id参数'}, status=400)
    
    account_history = get_mock_account_history(days) if use_mock else get_account_history_from_xt(account_id, days)
    
    if account_history is None:
        account_history = get_mock_account_history(days)
    
    result = calculate_volatility(account_history)
    result['is_mock'] = use_mock
    
    return JsonResponse(result)


@api_view(['GET'])
def get_max_drawdown(request):
    """
    最大回撤接口
    API路径: /api/risk-threshold/max-drawdown/
    """
    account_id = request.GET.get('account_id')
    days = int(request.GET.get('days', 30))
    use_mock = request.GET.get('mock', 'true').lower() == 'true'
    
    if not account_id:
        return JsonResponse({'success': False, 'error': '缺少account_id参数'}, status=400)
    
    account_history = get_mock_account_history(days) if use_mock else get_account_history_from_xt(account_id, days)
    
    if account_history is None:
        account_history = get_mock_account_history(days)
    
    result = calculate_max_drawdown(account_history)
    result['is_mock'] = use_mock
    
    return JsonResponse(result)


@api_view(['GET'])
def get_var_value(request):
    """
    VaR值接口
    API路径: /api/risk-threshold/var/
    """
    account_id = request.GET.get('account_id')
    days = int(request.GET.get('days', 30))
    confidence = float(request.GET.get('confidence', 0.95))
    use_mock = request.GET.get('mock', 'true').lower() == 'true'
    
    if not account_id:
        return JsonResponse({'success': False, 'error': '缺少account_id参数'}, status=400)
    
    account_history = get_mock_account_history(days) if use_mock else get_account_history_from_xt(account_id, days)
    
    if account_history is None:
        account_history = get_mock_account_history(days)
    
    result = calculate_var(account_history, confidence_level=confidence)
    result['is_mock'] = use_mock
    
    return JsonResponse(result)

