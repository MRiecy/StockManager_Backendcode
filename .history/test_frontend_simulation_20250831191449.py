#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模拟前端请求，测试认证系统
"""

import requests
import json
import time

# API基础URL
BASE_URL = "http://127.0.0.1:8000"

def test_frontend_simulation():
    """模拟前端请求流程"""
    print("=== 模拟前端请求流程 ===")
    
    # 生成唯一用户名
    timestamp = int(time.time())
    username = f"frontenduser{timestamp}"
    
    # 1. 注册用户
    print("1. 注册用户...")
    register_data = {
        "username": username,
        "password": "testpass123",
        "nickname": "前端测试用户",
        "phone": "13900139000"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/register/", json=register_data)
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            print("✅ 注册成功!")
            access_token = result['data']['token']['access_token']
            print(f"获取到access_token: {access_token[:20]}...")
        else:
            print(f"❌ 注册失败: {result.get('message', '未知错误')}")
            return
    else:
        print(f"❌ 注册请求失败: {response.status_code}")
        return
    
    # 2. 测试账户信息API（模拟前端的请求）
    print("\n2. 测试账户信息API...")
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    print(f"发送请求到: {BASE_URL}/api/account-info/")
    print(f"Authorization头: Bearer {access_token[:20]}...")
    
    response = requests.get(f"{BASE_URL}/api/account-info/", headers=headers)
    print(f"响应状态码: {response.status_code}")
    print(f"响应头: {dict(response.headers)}")
    
    if response.status_code == 200:
        result = response.json()
        print("✅ 账户信息API调用成功!")
        print(f"响应数据: {json.dumps(result, indent=2, ensure_ascii=False)}")
    else:
        print(f"❌ 账户信息API调用失败!")
        print(f"响应内容: {response.text}")
        
        # 如果是401错误，尝试诊断问题
        if response.status_code == 401:
            print("\n🔍 401错误诊断:")
            print("1. 检查token是否有效...")
            
            # 测试token是否真的有效
            profile_response = requests.get(f"{BASE_URL}/api/auth/profile/", headers=headers)
            if profile_response.status_code == 200:
                print("✅ Token本身是有效的（profile API成功）")
                print("❌ 问题可能在于account-info API的权限设置")
            else:
                print(f"❌ Token本身也无效: {profile_response.status_code}")
    
    # 3. 测试其他需要认证的API
    print("\n3. 测试其他认证API...")
    
    # 测试profile API
    profile_response = requests.get(f"{BASE_URL}/api/auth/profile/", headers=headers)
    print(f"Profile API状态码: {profile_response.status_code}")
    
    # 测试asset-category API
    asset_response = requests.get(f"{BASE_URL}/api/asset-category/", headers=headers)
    print(f"Asset Category API状态码: {asset_response.status_code}")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_frontend_simulation() 