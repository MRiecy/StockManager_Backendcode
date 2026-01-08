# 导入交易模块
from xtquant.xttrader import XtQuantTrader
import pandas as pd

# 指定本地miniqmt客户端路径
miniqmt_path = r'D:\国金QMT交易端模拟\userdata_mini'

# 会话id，个人使用随意设置即可
session_id = 123456

# 实例化交易连接对象
trader = XtQuantTrader(miniqmt_path, session_id)

# 启动交易线程
trader.start()

# 查看连接状态，0表示连接成功
trader.connect()
print(trader.connect())

# 导入账户模块
from xtquant.xttype import StockAccount

# 实例化账户对象
account = StockAccount('62283925')
asset_info = trader.query_stock_asset(account)

print(f'总资产：{asset_info.total_asset}')
print(f'可用金额：{asset_info.cash}')
print(f'持仓市值：{asset_info.market_value}')

positions_info = trader.query_stock_positions(account)

print(f'最新持仓标的数量：{len(positions_info)}')
print('具体持仓信息：')
print(pd.DataFrame(
    [
        {
            '证券代码': position.stock_code,
            '持仓数量': position.volume,
            '可用数量': position.can_use_volume
        }
        for position in positions_info
    ]
))

