"""
迅投连接测试与Django启动脚本
先测试迅投连接，确保连接成功后再启动Django服务器
"""
import os
import sys
import time
import subprocess
from xtquant.xttrader import XtQuantTrader, XtQuantTraderCallback

# 正确的迅投路径（从测试中确认）
XTQUANT_PATH = r'E:\迅投极速交易终端 睿智融科版\userdata'

class SimpleCallback(XtQuantTraderCallback):
    def on_disconnected(self):
        print("连接断开回调")

def test_xtquant_connection():
    """测试与迅投的连接"""
    print(f"\n测试迅投路径: {XTQUANT_PATH}")
    print(f"路径存在: {os.path.exists(XTQUANT_PATH)}")
    
    if not os.path.exists(XTQUANT_PATH):
        return False, "迅投路径不存在，请检查安装路径"
    
    try:
        # 创建交易接口实例
        session_id = int(time.time())
        print(f"使用会话ID: {session_id}")
        xt_trader = XtQuantTrader(XTQUANT_PATH, session_id)
        
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
                -1: "登录失败，请检查迅投配置，确保迅投交易终端已启动并登录",
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
            xt_trader.stop()
            return False, "登录成功但未查询到账户信息，请确认迅投账户状态"
        
        # 停止交易API
        print("停止XtQuantTrader...")
        xt_trader.stop()
        
        return True, f"迅投连接成功，检测到 {len(accounts)} 个账户"
        
    except Exception as e:
        print(f"异常: {str(e)}")
        return False, f"连接迅投时发生异常: {str(e)}"

def main():
    print("=" * 80)
    print(" 迅投连接测试与Django启动工具 ")
    print("=" * 80)
    
    # 测试迅投连接
    success, message = test_xtquant_connection()
    
    if success:
        print(f"\n✅ 迅投连接测试成功: {message}")
        
        # 确保Django配置文件使用正确的路径
        update_settings_path()
        
        # 启动Django服务器
        print("\n正在启动Django服务器...")
        try:
            subprocess.run([sys.executable, "manage.py", "runserver"])
        except KeyboardInterrupt:
            print("\nDjango服务器已停止")
        except Exception as e:
            print(f"\n启动Django服务器时出错: {str(e)}")
    else:
        print(f"\n❌ 迅投连接测试失败: {message}")
        print("\n请解决上述问题后再尝试启动Django服务器")
        input("\n按Enter键退出...")

def update_settings_path():
    """更新Django设置文件中的迅投路径"""
    try:
        settings_path = os.path.join("StockManager_Backendcode", "settings.py")
        
        # 读取设置文件
        if os.path.exists(settings_path):
            with open(settings_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # 检查当前路径配置
            if f"'USERDATA_PATH': r'{XTQUANT_PATH}'" not in content:
                print(f"\n⚠️ 注意: 建议在 settings.py 中将 USERDATA_PATH 设置为: {XTQUANT_PATH}")
        else:
            print(f"\n⚠️ 警告: 找不到设置文件 {settings_path}")
    except Exception as e:
        print(f"\n检查设置文件时出错: {str(e)}")

if __name__ == "__main__":
    main() 