import numpy as np
from datetime import datetime, timedelta


def get_total_shares(stock_code):
    """
    获取股票总股本数据
    """
    # 模拟数据，实际应从数据源获取
    return 10000000  # 返回1000万股作为默认值


def get_operating_assets(account_id):
    """
    获取账户的营运资产
    """
    # 模拟数据，实际应从数据库获取
    return 5000000  # 返回500万作为默认值


def get_empirical_percentage(account_id):
    """
    获取经验性百分比率
    """
    # 模拟数据，实际应根据业务规则计算
    return 0.7  # 返回70%作为默认值


def get_futures_contract_size(futures_code):
    """
    获取期货合约规模
    """
    # 模拟数据，实际应从数据源获取
    contract_sizes = {
        'IF': 300,  # 沪深300指数期货
        'IC': 200,  # 中证500指数期货
        'IH': 300,  # 上证50指数期货
        'T': 10000,  # 10年期国债期货
        'TF': 10000,  # 5年期国债期货
        'TS': 10000,  # 2年期国债期货
    }
    
    # 提取期货品种代码
    for code_prefix in contract_sizes:
        if futures_code.startswith(code_prefix):
            return contract_sizes[code_prefix]
    
    # 默认返回
    return 1


def get_trades(account_id, stock_code):
    """
    获取账户的成交记录
    """
    # 模拟数据，实际应从数据库获取
    class Trade:
        def __init__(self, price, volume):
            self.price = price
            self.volume = volume
    
    # 返回模拟的成交记录
    return [
        Trade(100, 100),
        Trade(101, 200),
        Trade(99, 150)
    ]


def calculate_market_value(position, asset_type):
    """
    计算各类资产的市场额
    """
    if asset_type == 'stock':
        # 股票市场额 = 股票价格 × 总股本
        total_shares = get_total_shares(position.stock_code)
        return position.current_price * total_shares

    elif asset_type == 'credit':
        # 信用市场额 = 信用限额 = 营运资产 × 经验性百分比率
        operating_assets = get_operating_assets(position.account_id)
        empirical_percentage = get_empirical_percentage(position.account_id)
        return operating_assets * empirical_percentage

    elif asset_type == 'futures':
        # 期货市场额 = 合约价格 × 合约规模 × 成交手数
        contract_size = get_futures_contract_size(position.stock_code)
        return position.current_price * contract_size * position.volume

    elif asset_type in ['futures_options', 'stock_options']:
        # 期权市场额 = 期权权利金 × 合约单位 × 成交手数
        contract_unit = 100 if asset_type == 'stock_options' else get_futures_contract_size(position.stock_code)
        return position.current_price * contract_unit * position.volume

    elif asset_type in ['sh_hk_connect', 'sz_hk_connect']:
        # 港股通市场额 = ∑(成交价格 × 成交数量)
        # 需要从成交记录中获取
        trades = get_trades(position.account_id, position.stock_code)
        return sum(trade.price * trade.volume for trade in trades)

    return 0


def get_category_start_value(acc, category):
    """
    获取资产类别的期初价值
    """
    # 模拟数据，实际应从数据库获取历史数据
    default_values = {
        'stock': 5000000,
        'credit': 3000000,
        'futures': 2000000,
        'futures_options': 1000000,
        'stock_options': 1500000,
        'sh_hk_connect': 2500000,
        'sz_hk_connect': 2000000
    }
    
    return default_values.get(category, 0)


def get_account_history(acc, period):
    """
    获取账户历史资产数据
    """
    # 模拟数据，实际应从数据库获取
    result = []
    base_value = 1000000
    
    if period == 'weekly':
        for i in range(1, 5):  # 过去4周
            date = (datetime.now() - timedelta(weeks=i))
            result.append({
                'period': f'Week {i} ({date.strftime("%Y-%m-%d")})',
                'total_assets': base_value * (1 + 0.02 * i),
                'start_value': base_value,
                'end_value': base_value * (1 + 0.02 * i),
                'market_value': base_value * (1 + 0.02 * i) * 0.9
            })
    else:  # yearly
        for i in range(1, 6):  # 过去5年
            year = datetime.now().year - i
            result.append({
                'period': f'Year {year}',
                'total_assets': base_value * (1 + 0.1 * i),
                'start_value': base_value,
                'end_value': base_value * (1 + 0.1 * i),
                'market_value': base_value * (1 + 0.1 * i) * 0.9
            })
    
    return result


def get_total_assets(accounts):
    """
    计算所有账户的总资产
    """
    total = 0
    for acc in accounts:
        asset = acc.total_asset if hasattr(acc, 'total_asset') else 0
        total += asset
    return total 