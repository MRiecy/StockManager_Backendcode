#!/usr/bin/env python
"""
API接口测试脚本
用于测试XtQuant连接和数据获取功能
"""
import os
import sys
import django
from pathlib import Path

# 添加项目路径
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'StockManager_Backendcode.settings')
django.setup()

import time
import traceback
from django.conf import settings
from xtquant.xttrader import XtQuantTrader, XtQuantTraderCallback
from xtquant.xttype import StockAccount

class TestXtQuantConnection:
    def __init__(self):
        self.xt_trader = None
        
    def test_connection(self):
        """测试XtQuant连接"""
        print("🔄 开始测试XtQuant连接...")
        
        try:
            # 获取配置
            path = settings.XT_CONFIG['USERDATA_PATH']
            print(f"📁 使用路径: {path}")
            
            # 检查路径是否存在
            if not os.path.exists(path):
                print(f"❌ 错误: 路径不存在 {path}")
                print("💡 请检查 .env 文件中的 XT_USERDATA_PATH 配置")
                return False
                
            # 创建交易接口
            session_id = int(time.time())
            self.xt_trader = XtQuantTrader(path, session_id)
            
            # 启动交易线程
            self.xt_trader.start()
            print("✅ 交易线程启动成功")
            
            # 建立连接
            connect_result = self.xt_trader.connect()
            if connect_result == 0:
                print("✅ XtQuant连接成功")
                return True
            else:
                print(f"❌ XtQuant连接失败，错误码: {connect_result}")
                return False
                
        except Exception as e:
            print(f"❌ 连接测试异常: {str(e)}")
            traceback.print_exc()
            return False
    
    def test_account_query(self, account_id="test_account"):
        """测试账户查询功能"""
        if not self.xt_trader:
            print("❌ 请先建立连接")
            return False
            
        try:
            print(f"🔄 测试账户查询功能...")
            
            # 查询所有账户
            accounts = self.xt_trader.query_account_infos()
            print(f"📊 查询到 {len(accounts)} 个账户")
            
            if accounts:
                for i, acc in enumerate(accounts):
                    print(f"  账户 {i+1}: {acc.account_id} ({acc.account_type})")
                    
                # 测试第一个账户的资产查询
                test_acc = accounts[0]
                asset = self.xt_trader.query_stock_asset(test_acc)
                if asset:
                    print(f"✅ 账户资产查询成功:")
                    print(f"  - 账户ID: {asset.account_id}")
                    print(f"  - 可用资金: {asset.cash}")
                    print(f"  - 总资产: {asset.total_asset}")
                    print(f"  - 持仓市值: {asset.market_value}")
                else:
                    print("⚠️ 未查询到资产信息")
                    
                return True
            else:
                print("⚠️ 未查询到账户信息")
                return False
                
        except Exception as e:
            print(f"❌ 账户查询异常: {str(e)}")
            traceback.print_exc()
            return False
    
    def cleanup(self):
        """清理资源"""
        if self.xt_trader:
            try:
                self.xt_trader.stop()
                print("✅ 连接已关闭")
            except:
                pass

def test_django_api_views():
    """测试Django API视图函数"""
    print("\n🔄 测试Django API视图...")
    
    try:
        # 测试导入视图函数
        from account.views import get_account_info
        from Comparison.views import asset_comparison
        
        print("✅ API视图函数导入成功:")
        print("  - account.views.get_account_info")
        print("  - Comparison.views.asset_comparison")
        
        return True
        
    except Exception as e:
        print(f"❌ API视图导入失败: {str(e)}")
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("🚀 开始API接口测试\n")
    
    # 测试配置
    print("📋 检查配置...")
    print(f"  - USERDATA_PATH: {settings.XT_CONFIG['USERDATA_PATH']}")
    print(f"  - TOKEN: {settings.XT_CONFIG['TOKEN'][:20]}...")
    print(f"  - API_KEY: {'已设置' if settings.XT_CONFIG['API_KEY'] else '未设置'}")
    print(f"  - SECRET_KEY: {'已设置' if settings.XT_CONFIG['SECRET_KEY'] else '未设置'}")
    print()
    
    # 测试Django视图
    django_test = test_django_api_views()
    print()
    
    # 测试XtQuant连接
    tester = TestXtQuantConnection()
    
    try:
        connection_test = tester.test_connection()
        
        if connection_test:
            print()
            account_test = tester.test_account_query()
        else:
            account_test = False
            
    finally:
        tester.cleanup()
    
    # 输出测试结果
    print("\n" + "="*50)
    print("📊 测试结果汇总:")
    print(f"  - Django视图导入: {'✅ 通过' if django_test else '❌ 失败'}")
    print(f"  - XtQuant连接: {'✅ 通过' if connection_test else '❌ 失败'}")
    print(f"  - 账户数据查询: {'✅ 通过' if account_test else '❌ 失败'}")
    
    if connection_test and account_test:
        print("\n🎉 所有测试通过！API接口可以正常使用")
        print("💡 下一步可以启动Django服务器进行完整测试")
    else:
        print("\n⚠️ 部分测试失败，请检查配置")
        if not connection_test:
            print("💡 建议检查:")
            print("  1. QMT客户端是否已启动")
            print("  2. USERDATA_PATH路径是否正确")
            print("  3. TOKEN是否有效")

if __name__ == "__main__":
    main()
