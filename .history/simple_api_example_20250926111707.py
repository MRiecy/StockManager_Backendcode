#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的API调用示例 - 自动触发数据下载
"""

import requests
import json
from datetime import datetime, timedelta

def download_stock_data():
    """通过API自动下载股票数据"""
    
    # API端点
    url = "http://localhost:8000/api/asset_comparison/"
    
    # 请求数据
    data = {
        "symbols": ["600519.SH", "000001.SZ"],  # 股票代码
        "period": "1d",                         # 日线数据
        "start_time": "2024-01-01 00:00:00",   # 开始时间
        "end_time": "2024-12-31 23:59:59"      # 结束时间
    }
    
    print("🚀 发送API请求...")
    print(f"📊 股票代码: {data['symbols']}")
    print(f"📅 时间范围: {data['start_time']} 到 {data['end_time']}")
    
    try:
        # 发送POST请求
        response = requests.post(url, json=data)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 请求成功!")
            
            # 显示结果
            for symbol, records in result.get('data', {}).items():
                print(f"\n📈 {symbol}:")
                print(f"   数据条数: {len(records)}")
                if records:
                    print(f"   最新价格: {records[-1].get('close', 'N/A')}")
                    print(f"   最新时间: {records[-1].get('time', 'N/A')}")
        else:
            print(f"❌ 请求失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            
    except Exception as e:
        print(f"❌ 发生错误: {str(e)}")

if __name__ == "__main__":
    download_stock_data()
