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