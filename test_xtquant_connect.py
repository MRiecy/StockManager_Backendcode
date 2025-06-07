"""
迅投连接测试脚本
用于测试与迅投接口的连接状态
"""
import os
import sys
import time
from xtquant.xttrader import XtQuantTrader, XtQuantTraderCallback

# 定义路径，测试多个可能的路径
paths_to_test = [
    r'E:\迅投极速交易终端 睿智融科版\userdata',  # 空格版本
    r'E:\迅投极速交易终端睿智融科版\userdata',   # 无空格版本
]

class SimpleCallback(XtQuantTraderCallback):
    def on_disconnected(self):
        print("连接断开回调")

def test_path(path):
    """测试特定路径的连接"""
    print(f"\n测试路径: {path}")
    print(f"路径存在: {os.path.exists(path)}")
    
    if not os.path.exists(path):
        return False, "路径不存在"
    
    try:
        # 创建交易接口实例
        session_id = int(time.time())
        print(f"使用会话ID: {session_id}")
        xt_trader = XtQuantTrader(path, session_id)
        
        # 注册回调
        callback = SimpleCallback()
        xt_trader.register_callback(callback)
        
        # 启动API
        print("启动XtQuantTrader...")
        xt_trader.start()
        
        # 建立交易连接
        print("尝试连接迅投交易接口...")
        connect_result = xt_trader.connect()
        print(f"连接结果: {connect_result}")
        
        if connect_result != 0:
            error_map = {
                -1: "登录失败，请检查迅投配置，确保迅投交易终端已登录",
                -2: "连接超时，请检查网络配置"
            }
            error_msg = error_map.get(connect_result, f"未知错误，错误码: {connect_result}")
            xt_trader.stop()
            return False, error_msg
        
        # 查询账户信息
        print("查询账户信息...")
        accounts = xt_trader.query_account_infos()
        
        if accounts:
            print(f"成功获取到 {len(accounts)} 个账户:")
            for acc in accounts:
                print(f"  - 账户ID: {acc.account_id}, 类型: {acc.account_type}")
        else:
            print("未查询到账户信息")
        
        # 停止交易API
        print("停止XtQuantTrader...")
        xt_trader.stop()
        
        return True, "连接成功" if accounts else "连接成功但未查询到账户信息"
        
    except Exception as e:
        print(f"异常: {str(e)}")
        return False, f"发生异常: {str(e)}"

def main():
    print("=" * 50)
    print("迅投连接测试工具")
    print("=" * 50)
    
    success = False
    
    # 测试各个路径
    for path in paths_to_test:
        result, message = test_path(path)
        if result:
            success = True
            print(f"\n✅ 路径 {path} 测试成功: {message}")
        else:
            print(f"\n❌ 路径 {path} 测试失败: {message}")
    
    if not success:
        print("\n所有路径都测试失败。请确保:")
        print("1. 迅投极速交易终端已启动并登录")
        print("2. userdata目录存在且可访问")
        print("3. 迅投账户已正确登录")
    
    print("\n测试完成")

if __name__ == "__main__":
    main() 