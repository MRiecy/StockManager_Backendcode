"""
模拟交易接口，当真实交易接口无法连接时使用
"""
class MockAccount:
    """模拟账户类"""
    def __init__(self, account_id, account_type="STOCK"):
        self.account_id = account_id
        self.account_type = account_type


class MockPosition:
    """模拟持仓类"""
    def __init__(self, stock_code, volume, current_price, avg_price, account_id="mock_account"):
        self.stock_code = stock_code
        self.volume = volume
        self.can_use_volume = volume
        self.current_price = current_price
        self.open_price = current_price
        self.avg_price = avg_price
        self.market_value = volume * current_price
        self.frozen_volume = 0
        self.on_road_volume = 0
        self.yesterday_volume = volume
        self.account_id = account_id
        self.account_type = "STOCK"


class MockAsset:
    """模拟资产类"""
    def __init__(self, account_id, cash=1000000, market_value=2000000):
        self.account_id = account_id
        self.account_type = "STOCK"
        self.cash = cash
        self.frozen_cash = 50000
        self.market_value = market_value
        self.total_asset = cash + market_value


class MockXtTrader:
    """模拟迅投交易接口"""
    def __init__(self):
        print("初始化模拟交易接口")
        self.accounts = [
            MockAccount("A123456789"),
            MockAccount("B123456789")
        ]
        self.positions = {
            "A123456789": [
                MockPosition("600000.SH", 10000, 12.5, 11.8, "A123456789"),
                MockPosition("000001.SZ", 5000, 15.2, 14.5, "A123456789"),
                MockPosition("601318.SH", 3000, 40.8, 38.2, "A123456789")
            ],
            "B123456789": [
                MockPosition("600036.SH", 8000, 35.6, 33.1, "B123456789"),
                MockPosition("002594.SZ", 12000, 18.7, 17.5, "B123456789")
            ]
        }
        self.assets = {
            "A123456789": MockAsset("A123456789", 1200000, 2500000),
            "B123456789": MockAsset("B123456789", 800000, 1800000)
        }

    def connect(self):
        """模拟连接"""
        return 0
        
    def start(self):
        """模拟启动"""
        pass
        
    def register_callback(self, callback):
        """模拟注册回调"""
        pass
        
    def query_account_infos(self):
        """查询所有账户信息"""
        return self.accounts
        
    def subscribe(self, account):
        """订阅账户"""
        return 0
        
    def query_stock_asset(self, account):
        """查询账户资产"""
        account_id = account.account_id
        if account_id in self.assets:
            return self.assets[account_id]
        return None
        
    def query_stock_positions(self, account):
        """查询账户持仓"""
        account_id = account.account_id
        if account_id in self.positions:
            return self.positions[account_id]
        return [] 