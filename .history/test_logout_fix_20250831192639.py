#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修复后的退出登录功能
"""

import requests
import json
import time

# API基础URL
BASE_URL = "http://127.0.0.1:8000"

def test_logout_fix():
    """测试修复后的退出登录功能"""
    print("=== 测试修复后的退出登录功能 ===")
    
    # 生成唯一用户名
    timestamp = int(time.time())
    username = f"logouttest{timestamp}"
    
    # 1. 先注册一个用户
    print("1. 注册用户...")
    register_data = {
        "username": username,
        "password": "testpass123",
        "nickname": "退出登录测试用户",
        "phone": "13600136000"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/register/", json=register_data)
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            print("✅ 注册成功!")
        else:
            print(f"❌ 注册失败: {result.get('message', '未知错误')}")
            return
    else:
        print(f"❌ 注册请求失败: {response.status_code}")
        return
    
    # 2. 登录用户
    print("\n2. 登录用户...")
    login_data = {
        "username": username,
        "password": "testpass123"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/login/", json=login_data)
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            print("✅ 登录成功!")
            access_token = result['data']['token']['access_token']
            print(f"获取到access_token: {access_token[:20]}...")
        else:
            print(f"❌ 登录失败: {result.get('message', '未知错误')}")
            return
    else:
        print(f"❌ 登录失败: {response.status_code}")
        return
    
    # 3. 测试正常退出登录（有有效token）
    print("\n3. 测试正常退出登录（有有效token）...")
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/logout/", headers=headers)
    print(f"响应状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            print("✅ 正常退出登录成功!")
            print(f"消息: {result.get('message', '未知')}")
        else:
            print(f"❌ 退出登录失败: {result.get('message', '未知错误')}")
    else:
        print(f"❌ 退出登录失败: {response.status_code}")
        print(f"响应内容: {response.text}")
    
    # 4. 测试使用已失效token退出登录
    print("\n4. 测试使用已失效token退出登录...")
    response = requests.post(f"{BASE_URL}/api/auth/logout/", headers=headers)
    print(f"响应状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            print("✅ 使用失效token退出登录成功!")
            print(f"消息: {result.get('message', '未知')}")
        else:
            print(f"❌ 退出登录失败: {result.get('message', '未知错误')}")
    else:
        print(f"❌ 退出登录失败: {response.status_code}")
        print(f"响应内容: {response.text}")
    
    # 5. 测试无token退出登录
    print("\n5. 测试无token退出登录...")
    response = requests.post(f"{BASE_URL}/api/auth/logout/")
    print(f"响应状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            print("✅ 无token退出登录成功!")
            print(f"消息: {result.get('message', '未知')}")
        else:
            print(f"❌ 退出登录失败: {result.get('message', '未知错误')}")
    else:
        print(f"❌ 退出登录失败: {response.status_code}")
        print(f"响应内容: {response.text}")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_logout_fix() 