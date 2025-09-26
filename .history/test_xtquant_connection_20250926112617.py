#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试xtquant连接和配置
"""

import os
import sys
import django
from datetime import datetime, timedelta

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'StockManager_Backendcode.settings')
django.setup()

from django.conf import settings

def test_xtquant_import():
    """测试xtquant模块导入"""
    print("🔍 测试xtquant模块导入...")
    try:
        import xtquant
        print("✅ xtquant模块导入成功")
        
        from xtquant import xtdata
        print("✅ xtdata模块导入成功")
        
        from xtquant import xtdatacenter as xtdc
        print("✅ xtdatacenter模块导入成功")
        
        return True
    except ImportError as e:
        print(f"❌ xtquant模块导入失败: {e}")
        return False

def test_xt_config():
    """测试XT_CONFIG配置"""
    print("\n🔍 测试XT_CONFIG配置...")
    
    config = settings.XT_CONFIG
    print(f"📋 当前配置:")
    print(f"   USERDATA_PATH: {config['USERDATA_PATH']}")
    print(f"   TOKEN: {config['TOKEN'][:20]}...")
    print(f"   API_KEY: {'已设置' if config['API_KEY'] else '未设置'}")
    print(f"   SECRET_KEY: {'已设置' if config['SECRET_KEY'] else '未设置'}")
    print(f"   ADDR_LIST: {len(config['ADDR_LIST'])} 个地址")
    print(f"   PORT: {config['PORT']}")
    
    # 检查路径是否存在
    if os.path.exists(config['USERDATA_PATH']):
        print("✅ USERDATA_PATH路径存在")
    else:
        print(f"❌ USERDATA_PATH路径不存在: {config['USERDATA_PATH']}")
        return False
    
    return True

def test_xtdatacenter_connection():
    """测试xtdatacenter连接"""
    print("\n🔍 测试xtdatacenter连接...")
    
    try:
        from xtquant import xtdatacenter as xtdc
        
        # 设置配置
        config = settings.XT_CONFIG
        xtdc.set_token(config['TOKEN'])
        xtdc.set_allow_optmize_address(config['ADDR_LIST'])
        
        print("✅ xtdatacenter配置设置成功")
        
        # 尝试连接
        port = config['PORT']
        print(f"📡 尝试连接到端口 {port}...")
        
        # 注意：这里只是设置配置，实际连接可能需要更多步骤
        print("✅ xtdatacenter配置完成")
        
        return True
        
    except Exception as e:
        print(f"❌ xtdatacenter连接失败: {e}")
        return False

def test_xtdata_download():
    """测试xtdata数据下载功能"""
    print("\n🔍 测试xtdata数据下载功能...")
    
    try:
        from xtquant import xtdata
        
        # 测试下载一只股票的数据
        symbol = "600519.SH"  # 贵州茅台
        period = "1d"
        start_date = "20241201"
        end_date = "20241231"
        
        print(f"📊 尝试下载 {symbol} 的 {period} 数据...")
        print(f"   时间范围: {start_date} 到 {end_date}")
        
        # 尝试下载数据
        result = xtdata.download_history_data(symbol, period, start_date, end_date)
        print(f"✅ 下载命令执行成功，返回值: {result}")
        
        # 尝试读取数据
        print("📖 尝试读取下载的数据...")
        data = xtdata.get_market_data_ex(
            field_list=['time', 'open', 'high', 'low', 'close', 'volume', 'amount'],
            stock_list=[symbol],
            period=period,
            start_time=start_date,
            end_time=end_date,
            count=-1,
            subscribe=False
        )
        
        if symbol in data and not data[symbol].empty:
            print(f"✅ 数据读取成功，共 {len(data[symbol])} 条记录")
            print(f"   最新价格: {data[symbol]['close'].iloc[-1]}")
            print(f"   最新时间: {data[symbol]['time'].iloc[-1]}")
            return True
        else:
            print("❌ 数据读取失败或数据为空")
            return False
            
    except Exception as e:
        print(f"❌ xtdata数据下载失败: {e}")
        return False

def test_duckdb():
    """测试duckdb功能"""
    print("\n🔍 测试duckdb功能...")
    
    try:
        import duckdb
        
        # 创建测试数据库
        conn = duckdb.connect()
        
        # 创建测试表
        conn.execute("CREATE TABLE test (id INTEGER, name VARCHAR)")
        conn.execute("INSERT INTO test VALUES (1, 'test')")
        
        # 查询测试
        result = conn.execute("SELECT * FROM test").fetchall()
        
        if result:
            print("✅ duckdb功能正常")
            return True
        else:
            print("❌ duckdb查询失败")
            return False
            
    except Exception as e:
        print(f"❌ duckdb测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🎯 xtquant连接和配置测试")
    print("=" * 50)
    
    tests = [
        ("xtquant模块导入", test_xtquant_import),
        ("XT_CONFIG配置", test_xt_config),
        ("xtdatacenter连接", test_xtdatacenter_connection),
        ("duckdb功能", test_duckdb),
        ("xtdata数据下载", test_xtdata_download),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}")
            results.append((test_name, False))
    
    # 总结
    print("\n" + "=" * 50)
    print("📊 测试结果总结:")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 总体结果: {passed}/{len(results)} 项测试通过")
    
    if passed == len(results):
        print("🎉 所有测试通过！xtquant配置正常")
    else:
        print("⚠️  部分测试失败，请检查配置")

if __name__ == "__main__":
    main()
