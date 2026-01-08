"""
简单的路径测试脚本 - 不依赖 Django
直接测试 userdata 路径是否可读
"""
import os

def test_userdata_path():
    """测试 userdata 路径"""
    # 直接使用配置的路径
    userdata_path = r'D:\迅投极速交易终端 睿智融科版\userdata'
    
    print("=" * 60)
    print("测试迅投 userdata 路径")
    print("=" * 60)
    print(f"测试路径: {userdata_path}")
    print()
    
    # 1. 检查路径是否存在
    print("1. 检查路径是否存在...")
    if os.path.exists(userdata_path):
        print("   [OK] 路径存在")
    else:
        print("   [FAIL] 路径不存在")
        return
    
    # 2. 检查是否是目录
    print("\n2. 检查是否是目录...")
    if os.path.isdir(userdata_path):
        print("   [OK] 是一个目录")
    else:
        print("   [FAIL] 不是一个目录")
        return
    
    # 3. 检查是否可读
    print("\n3. 检查是否可读...")
    if os.access(userdata_path, os.R_OK):
        print("   [OK] 目录可读")
    else:
        print("   [FAIL] 目录不可读（权限问题）")
        return
    
    # 4. 列出目录中的文件
    print("\n4. 列出目录中的文件...")
    try:
        files = os.listdir(userdata_path)
        print(f"   [OK] 目录中有 {len(files)} 个文件/文件夹")
        print()
        print("   前20个文件/文件夹:")
        for i, f in enumerate(files[:20], 1):
            file_path = os.path.join(userdata_path, f)
            try:
                if os.path.isfile(file_path):
                    file_size = os.path.getsize(file_path)
                    print(f"   {i:2d}. [文件] {f} ({file_size:,} bytes)")
                elif os.path.isdir(file_path):
                    print(f"   {i:2d}. [目录] {f}/")
                else:
                    print(f"   {i:2d}. [其他] {f}")
            except Exception as e:
                print(f"   {i:2d}. {f} (无法访问: {str(e)})")
    except Exception as e:
        print(f"   [FAIL] 无法列出目录内容: {str(e)}")
        import traceback
        traceback.print_exc()
        return
    
    # 5. 尝试使用迅投 SDK 读取（如果已安装）
    print()
    print("=" * 60)
    print("测试迅投 SDK 是否能使用该路径")
    print("=" * 60)
    
    try:
        from xtquant.xttrader import XtQuantTrader
        import time
        
        session_id = int(time.time())
        print(f"尝试创建 XtQuantTrader 对象...")
        print(f"  路径: {userdata_path}")
        print(f"  会话ID: {session_id}")
        
        try:
            trader = XtQuantTrader(userdata_path, session_id)
            print("  [OK] XtQuantTrader 对象创建成功")
            
            # 尝试启动（但不连接，避免阻塞）
            print("尝试启动交易接口...")
            trader.start()
            print("  [OK] 交易接口启动成功")
            print()
            print("  [NOTE] 注意：这只是测试创建和启动，实际连接需要有效的Token和授权")
            
        except Exception as e:
            print(f"  [FAIL] 创建或启动失败: {str(e)}")
            print(f"  错误类型: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            
    except ImportError as e:
        print(f"  [WARN] 无法导入迅投 SDK: {str(e)}")
        print("  请确保已安装 xtquant 包")
    except Exception as e:
        print(f"  [FAIL] 测试异常: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print()
    print("=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == '__main__':
    test_userdata_path()

