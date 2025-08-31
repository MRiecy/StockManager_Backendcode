#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修复后的登录功能
"""

import requests
import json
import time

# API基础URL
BASE_URL = "http://127.0.0.1:8000"

def test_login_fix():
    """测试修复后的登录功能"""
    print("=== 测试修复后的登录功能 ===")
    
    # 生成唯一用户名
    timestamp = int(time.time())
    username = f"logintest{timestamp}"
    
    # 1. 先注册一个用户
    print("1. 注册用户...")
    register_data = {
        "username": username,
        "password": "testpass123",
        "nickname": "登录测试用户",
        "phone": "13700137000"
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
    
    # 2. 测试使用username字段登录
    print("\n2. 测试使用username字段登录...")
    login_data_username = {
        "username": username,
        "password": "testpass123"
    }
    
    print(f"发送登录数据: {json.dumps(login_data_username, ensure_ascii=False)}")
    
    response = requests.post(f"{BASE_URL}/api/auth/login/", json=login_data_username)
    print(f"响应状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            print("✅ 使用username字段登录成功!")
            access_token = result['data']['token']['access_token']
            print(f"获取到access_token: {access_token[:20]}...")
        else:
            print(f"❌ 登录失败: {result.get('message', '未知错误')}")
            return
    else:
        print(f"❌ 登录失败: {response.status_code}")
        print(f"响应内容: {response.text}")
        return
    
    # 3. 测试使用username_or_phone字段登录
    print("\n3. 测试使用username_or_phone字段登录...")
    login_data_phone = {
        "username_or_phone": username,
        "password": "testpass123"
    }
    
    print(f"发送登录数据: {json.dumps(login_data_phone, ensure_ascii=False)}")
    
    response = requests.post(f"{BASE_URL}/api/auth/login/", json=login_data_phone)
    print(f"响应状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            print("✅ 使用username_or_phone字段登录成功!")
            access_token = result['data']['token']['access_token']
            print(f"获取到access_token: {access_token[:20]}...")
        else:
            print(f"❌ 登录失败: {result.get('message', '未知错误')}")
    else:
        print(f"❌ 登录失败: {response.status_code}")
        print(f"响应内容: {response.text}")
    
    # 4. 测试错误的密码
    print("\n4. 测试错误的密码...")
    login_data_wrong = {
        "username": username,
        "password": "wrongpassword"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/login/", json=login_data_wrong)
    print(f"响应状态码: {response.status_code}")
    
    if response.status_code == 400:
        result = response.json()
        print(f"✅ 错误密码被正确拒绝: {result.get('message', '未知错误')}")
    else:
        print(f"❌ 错误密码没有被正确拒绝: {response.status_code}")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_login_fix() 