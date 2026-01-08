"""
股票信息工具模块
用于获取股票的基本信息（名称、地区等）
"""

import logging
from xtquant import xtdata

logger = logging.getLogger(__name__)

# 股票地区映射表（基于股票代码）
# 上海：600xxx, 601xxx, 603xxx, 605xxx, 688xxx
# 深圳：000xxx, 001xxx, 002xxx, 300xxx
STOCK_REGION_MAP = {
    'SH': '上海',  # 上海证券交易所
    'SZ': '深圳',  # 深圳证券交易所
    'BJ': '北京',  # 北京证券交易所
}

# 股票行业分类映射（简化版本，实际应该从数据库或API获取）
STOCK_INDUSTRY_MAP = {
    # 这里可以添加更多的股票代码到行业的映射
    # 实际应用中应该从数据库或API获取
}


def get_stock_name(stock_code):
    """
    获取股票名称
    
    参数:
        stock_code: 股票代码（如 "600519.SH"）
    
    返回:
        str: 股票名称，如果获取失败返回股票代码
    """
    try:
        instrument_detail = xtdata.get_instrument_detail(stock_code)
        if instrument_detail and hasattr(instrument_detail, 'InstrumentName'):
            return instrument_detail.InstrumentName
        else:
            logger.warning(f'无法获取股票 {stock_code} 的名称')
            return stock_code
    except Exception as e:
        logger.warning(f'获取股票 {stock_code} 名称失败: {str(e)}')
        return stock_code


def get_stock_region(stock_code):
    """
    获取股票上市地区
    
    参数:
        stock_code: 股票代码（如 "600519.SH"）
    
    返回:
        str: 地区名称（如 "上海"、"深圳"）
    """
    try:
        # 从股票代码中提取市场代码
        if '.' in stock_code:
            market_code = stock_code.split('.')[-1]
            return STOCK_REGION_MAP.get(market_code, '其他')
        else:
            # 如果没有市场代码，根据股票代码前缀判断
            code_prefix = stock_code[:3]
            if code_prefix.startswith('600') or code_prefix.startswith('601') or code_prefix.startswith('603') or code_prefix.startswith('605') or code_prefix.startswith('688'):
                return '上海'
            elif code_prefix.startswith('000') or code_prefix.startswith('001') or code_prefix.startswith('002') or code_prefix.startswith('300'):
                return '深圳'
            else:
                return '其他'
    except Exception as e:
        logger.warning(f'获取股票 {stock_code} 地区失败: {str(e)}')
        return '其他'


def get_stock_industry(stock_code):
    """
    获取股票所属行业
    
    参数:
        stock_code: 股票代码（如 "600519.SH"）
    
    返回:
        str: 行业名称
    """
    try:
        # 如果映射表中有，直接返回
        if stock_code in STOCK_INDUSTRY_MAP:
            return STOCK_INDUSTRY_MAP[stock_code]
        
        # 否则尝试从API获取
        instrument_detail = xtdata.get_instrument_detail(stock_code)
        if instrument_detail and hasattr(instrument_detail, 'IndustryName'):
            return instrument_detail.IndustryName
        else:
            return '其他'
    except Exception as e:
        logger.warning(f'获取股票 {stock_code} 行业失败: {str(e)}')
        return '其他'










