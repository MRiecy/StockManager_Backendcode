#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API自动触发数据下载功能测试脚本
演示如何通过API接口自动下载股票数据
"""

import requests
import json
import time
from datetime import datetime, timedelta

# 配置
BASE_URL = "http://localhost:8000"
API_ENDPOINT = f"{BASE_URL}/api/asset_comparison/"

# 测试用的股票代码
TEST_SYMBOLS = [
    "600519.SH",  # 贵州茅台
    "000001.SZ",  # 平安银行
    "000002.SZ",  # 万科A
]

def test_api_download():
    """测试API自动触发数据下载功能"""
    
    print("🚀 开始测试API自动触发数据下载功能")
    print("=" * 60)
    
    # 1. 测试数据：请求最近30天的日线数据
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    request_data = {
        "symbols": TEST_SYMBOLS,
        "period": "1d",  # 日线数据
        "start_time": start_date.strftime("%Y-%m-%d %H:%M:%S"),
        "end_time": end_date.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    print(f"📊 请求参数:")
    print(f"   股票代码: {request_data['symbols']}")
    print(f"   时间周期: {request_data['period']}")
    print(f"   开始时间: {request_data['start_time']}")
    print(f"   结束时间: {request_data['end_time']}")
    print()
    
    try:
        # 2. 发送POST请求到API
        print("📡 发送API请求...")
        response = requests.post(
            API_ENDPOINT,
            json=request_data,
            headers={
                "Content-Type": "application/json",
                # 如果需要认证，添加Authorization头
                # "Authorization": "Bearer YOUR_TOKEN_HERE"
            },
            timeout=30  # 30秒超时
        )
        
        print(f"📈 响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API请求成功!")
            print()
            
            # 3. 分析返回的数据
            print("📋 返回数据分析:")
            print(f"   响应代码: {result.get('code', 'N/A')}")
            print(f"   消息: {result.get('message', 'N/A')}")
            
            if 'meta' in result:
                meta = result['meta']
                print(f"   数据点统计:")
                for symbol, count in meta.get('data_points', {}).items():
                    print(f"     {symbol}: {count} 条数据")
            
            print()
            
            # 4. 显示每个股票的详细数据
            if 'data' in result:
                print("📊 详细数据预览:")
                for symbol, data_list in result['data'].items():
                    print(f"\n   {symbol}:")
                    if data_list:
                        # 显示前3条和后3条数据
                        print(f"     总数据量: {len(data_list)} 条")
                        print(f"     最新3条数据:")
                        for i, record in enumerate(data_list[-3:]):
                            print(f"       {i+1}. 时间: {record.get('time', 'N/A')}, "
                                  f"收盘价: {record.get('close', 'N/A')}")
                    else:
                        print(f"     无数据")
            
            print()
            print("🎉 测试完成! 数据下载功能正常工作")
            
        else:
            print(f"❌ API请求失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 连接失败: 请确保Django服务器正在运行")
        print("   启动命令: conda activate ssc && python manage.py runserver")
        
    except requests.exceptions.Timeout:
        print("❌ 请求超时: 数据下载可能需要更长时间")
        
    except Exception as e:
        print(f"❌ 发生错误: {str(e)}")

def test_different_periods():
    """测试不同时间周期的数据下载"""
    
    print("\n" + "=" * 60)
    print("🔄 测试不同时间周期的数据下载")
    print("=" * 60)
    
    periods = ["1d", "1h", "30m", "5m"]
    symbols = ["600519.SH"]  # 只测试一只股票
    
    for period in periods:
        print(f"\n📊 测试周期: {period}")
        
        request_data = {
            "symbols": symbols,
            "period": period,
            "start_time": (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S"),
            "end_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        try:
            response = requests.post(API_ENDPOINT, json=request_data, timeout=15)
            if response.status_code == 200:
                result = response.json()
                data_count = len(result.get('data', {}).get(symbols[0], []))
                print(f"   ✅ 成功获取 {data_count} 条数据")
            else:
                print(f"   ❌ 失败: {response.status_code}")
        except Exception as e:
            print(f"   ❌ 错误: {str(e)}")

def test_cache_behavior():
    """测试缓存行为 - 重复请求应该更快"""
    
    print("\n" + "=" * 60)
    print("💾 测试缓存行为")
    print("=" * 60)
    
    request_data = {
        "symbols": ["600519.SH"],
        "period": "1d",
        "start_time": (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d %H:%M:%S"),
        "end_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # 第一次请求
    print("🔄 第一次请求 (可能触发下载)...")
    start_time = time.time()
    try:
        response1 = requests.post(API_ENDPOINT, json=request_data, timeout=30)
        time1 = time.time() - start_time
        print(f"   耗时: {time1:.2f} 秒")
    except Exception as e:
        print(f"   错误: {str(e)}")
        return
    
    # 等待一下
    time.sleep(2)
    
    # 第二次请求 (应该从缓存读取)
    print("🔄 第二次请求 (应该从缓存读取)...")
    start_time = time.time()
    try:
        response2 = requests.post(API_ENDPOINT, json=request_data, timeout=15)
        time2 = time.time() - start_time
        print(f"   耗时: {time2:.2f} 秒")
        
        if time2 < time1:
            print("   ✅ 缓存生效，第二次请求更快")
        else:
            print("   ⚠️  缓存可能未生效")
            
    except Exception as e:
        print(f"   错误: {str(e)}")

if __name__ == "__main__":
    print("🎯 API自动触发数据下载功能测试")
    print("=" * 60)
    print("📝 说明:")
    print("   1. 此脚本会测试API自动下载股票数据的功能")
    print("   2. 首次请求会触发数据下载")
    print("   3. 后续请求会从缓存读取，速度更快")
    print("   4. 请确保Django服务器正在运行")
    print()
    
    # 运行测试
    test_api_download()
    test_different_periods()
    test_cache_behavior()
    
    print("\n" + "=" * 60)
    print("🏁 所有测试完成!")
    print("💡 提示: 查看Django服务器日志可以看到数据下载过程")
