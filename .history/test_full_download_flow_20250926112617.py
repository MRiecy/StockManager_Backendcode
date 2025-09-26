#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试完整的数据下载流程
"""

import os
import sys
import django
from datetime import datetime, timedelta

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'StockManager_Backendcode.settings')
django.setup()

from django.conf import settings
from apps.Comparison.services import get_combined_market_data
from apps.Comparison.models import CacheIndex

def test_download_flow():
    """测试完整的数据下载流程"""
    print("🎯 测试完整的数据下载流程")
    print("=" * 50)
    
    # 测试参数
    symbols = ["600519.SH"]
    period = "1d"
    start_time = datetime(2024, 12, 1)
    end_time = datetime(2024, 12, 31)
    
    print(f"📊 测试参数:")
    print(f"   股票代码: {symbols}")
    print(f"   时间周期: {period}")
    print(f"   开始时间: {start_time}")
    print(f"   结束时间: {end_time}")
    print()
    
    # 检查缓存状态
    print("🔍 检查缓存状态...")
    cache_entries = CacheIndex.objects.filter(symbol=symbols[0], period=period)
    print(f"   缓存记录数: {cache_entries.count()}")
    
    for entry in cache_entries:
        print(f"   - {entry.symbol} {entry.period}: {entry.start_date} 到 {entry.end_date}")
        print(f"     文件路径: {entry.file_path}")
        print(f"     文件存在: {os.path.exists(entry.file_path)}")
    
    print()
    
    # 调用核心函数
    print("🚀 调用 get_combined_market_data...")
    try:
        result = get_combined_market_data(symbols, period, start_time, end_time)
        
        print(f"✅ 函数调用成功")
        print(f"   返回结果类型: {type(result)}")
        print(f"   结果键: {list(result.keys())}")
        
        for symbol, df in result.items():
            print(f"\n📈 {symbol}:")
            print(f"   数据类型: {type(df)}")
            print(f"   数据形状: {df.shape if hasattr(df, 'shape') else 'N/A'}")
            print(f"   数据条数: {len(df) if hasattr(df, '__len__') else 'N/A'}")
            
            if hasattr(df, 'head') and not df.empty:
                print(f"   前3条数据:")
                print(df.head(3).to_string())
            elif not df.empty:
                print(f"   数据内容: {df}")
        
        # 再次检查缓存
        print(f"\n🔍 调用后缓存状态...")
        cache_entries_after = CacheIndex.objects.filter(symbol=symbols[0], period=period)
        print(f"   缓存记录数: {cache_entries_after.count()}")
        
        for entry in cache_entries_after:
            print(f"   - {entry.symbol} {entry.period}: {entry.start_date} 到 {entry.end_date}")
            print(f"     文件路径: {entry.file_path}")
            print(f"     文件存在: {os.path.exists(entry.file_path)}")
            if os.path.exists(entry.file_path):
                print(f"     文件大小: {os.path.getsize(entry.file_path)} 字节")
        
        return True
        
    except Exception as e:
        print(f"❌ 函数调用失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_manual_download():
    """手动测试下载功能"""
    print("\n" + "=" * 50)
    print("🔧 手动测试下载功能")
    print("=" * 50)
    
    try:
        from xtquant import xtdata
        
        symbol = "600519.SH"
        period = "1d"
        start_date = "20241201"
        end_date = "20241231"
        
        print(f"📊 手动下载 {symbol} 数据...")
        print(f"   时间范围: {start_date} 到 {end_date}")
        
        # 下载数据
        result = xtdata.download_history_data(symbol, period, start_date, end_date)
        print(f"   下载结果: {result}")
        
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
            print(f"   数据列: {list(df.columns)}")
            print(f"   前3条数据:")
            print(df.head(3).to_string())
            return True
        else:
            print("❌ 数据读取失败或数据为空")
            return False
            
    except Exception as e:
        print(f"❌ 手动下载失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("🎯 完整数据下载流程测试")
    print("=" * 50)
    
    # 测试手动下载
    manual_success = test_manual_download()
    
    # 测试完整流程
    flow_success = test_download_flow()
    
    print("\n" + "=" * 50)
    print("📊 测试结果总结:")
    print("=" * 50)
    print(f"   手动下载: {'✅ 成功' if manual_success else '❌ 失败'}")
    print(f"   完整流程: {'✅ 成功' if flow_success else '❌ 失败'}")
    
    if manual_success and flow_success:
        print("🎉 所有测试通过！数据下载功能正常")
    else:
        print("⚠️  部分测试失败，需要进一步调试")

if __name__ == "__main__":
    main()
