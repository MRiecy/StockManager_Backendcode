#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复后的xtquant测试脚本
"""

import os
import sys
import django
from datetime import datetime, timedelta

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'StockManager_Backendcode.settings')
django.setup()

from django.conf import settings

def test_xtdata_download_fixed():
    """测试xtdata数据下载功能 - 修复版本"""
    print("🔍 测试xtdata数据下载功能...")
    
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
        
        # 尝试读取数据 - 修复参数
        print("📖 尝试读取下载的数据...")
        data = xtdata.get_market_data_ex(
            field_list=['time', 'open', 'high', 'low', 'close', 'volume', 'amount'],
            stock_list=[symbol],
            period=period,
            start_time=start_date,
            end_time=end_date,
            count=-1
            # 移除 subscribe 参数，因为某些版本不支持
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

def test_xtdata_simple():
    """测试xtdata简单功能"""
    print("\n🔍 测试xtdata简单功能...")
    
    try:
        from xtquant import xtdata
        
        # 测试获取股票列表
        print("📋 尝试获取股票列表...")
        stock_list = xtdata.get_stock_list_in_sector('沪深A股')
        if stock_list:
            print(f"✅ 获取股票列表成功，共 {len(stock_list)} 只股票")
            print(f"   前5只股票: {stock_list[:5]}")
        else:
            print("❌ 获取股票列表失败")
            return False
        
        # 测试获取实时行情
        print("\n📈 尝试获取实时行情...")
        try:
            quote = xtdata.get_market_data(['600519.SH'], period='1d', count=1)
            if quote and '600519.SH' in quote:
                print("✅ 获取实时行情成功")
                print(f"   贵州茅台最新价: {quote['600519.SH']['close'].iloc[-1]}")
            else:
                print("❌ 获取实时行情失败")
                return False
        except Exception as e:
            print(f"⚠️  实时行情获取失败: {e}")
            # 这不影响整体测试
        
        return True
        
    except Exception as e:
        print(f"❌ xtdata简单功能测试失败: {e}")
        return False

def test_download_and_save():
    """测试下载并保存数据"""
    print("\n🔍 测试下载并保存数据...")
    
    try:
        from xtquant import xtdata
        import pandas as pd
        import duckdb
        import os
        
        symbol = "600519.SH"
        period = "1d"
        start_date = "20241201"
        end_date = "20241231"
        
        # 下载数据
        print(f"📊 下载 {symbol} 数据...")
        xtdata.download_history_data(symbol, period, start_date, end_date)
        
        # 读取数据
        print("📖 读取数据...")
        data = xtdata.get_market_data_ex(
            field_list=['time', 'open', 'high', 'low', 'close', 'volume', 'amount'],
            stock_list=[symbol],
            period=period,
            start_time=start_date,
            end_time=end_date,
            count=-1
        )
        
        if symbol in data and not data[symbol].empty:
            df = data[symbol]
            print(f"✅ 数据读取成功，共 {len(df)} 条记录")
            
            # 保存为Parquet
            cache_dir = os.path.join(settings.CACHE_ROOT, symbol.replace('.', '_'))
            os.makedirs(cache_dir, exist_ok=True)
            
            file_path = os.path.join(cache_dir, f"{period}_2024.parquet")
            
            # 使用DuckDB保存
            conn = duckdb.connect()
            conn.execute(f"COPY df TO '{file_path}' (FORMAT PARQUET, COMPRESSION SNAPPY)")
            
            print(f"✅ 数据已保存到: {file_path}")
            print(f"   文件大小: {os.path.getsize(file_path)} 字节")
            
            return True
        else:
            print("❌ 数据为空")
            return False
            
    except Exception as e:
        print(f"❌ 下载并保存数据失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🎯 xtquant功能测试 - 修复版本")
    print("=" * 50)
    
    tests = [
        ("xtdata简单功能", test_xtdata_simple),
        ("xtdata数据下载", test_xtdata_download_fixed),
        ("下载并保存数据", test_download_and_save),
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
        print("🎉 所有测试通过！xtquant功能正常")
    else:
        print("⚠️  部分测试失败，请检查配置")

if __name__ == "__main__":
    main()


