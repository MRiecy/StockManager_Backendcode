#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试所有认证API的完整功能
"""

import requests
import json
import time

# API基础URL
BASE_URL = "http://127.0.0.1:8000"

def test_all_auth_apis():
    """测试所有认证API"""
    print("=== 测试所有认证API ===")
    
    # 生成唯一用户名
    timestamp = int(time.time())
    username = f"testuser{timestamp}"
    password = "testpass123"
    
    print(f"测试用户名: {username}")
    print(f"测试密码: {password}")
    
    # 1. 测试用户注册
    print("\n1. 测试用户注册...")
    register_data = {
        "username": username,
        "password": password,
        "nickname": "测试用户",
        "phone": "13800138000"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/register/", json=register_data)
    print(f"注册响应状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            print("✅ 注册成功!")
            access_token = result['data']['token']['access_token']
            refresh_token = result['data']['token']['refresh_token']
            print(f"用户ID: {result['data']['user']['id']}")
            print(f"用户名: {result['data']['user']['username']}")
        else:
            print(f"❌ 注册失败: {result.get('message', '未知错误')}")
            return
    else:
        print(f"❌ 注册请求失败: {response.status_code}")
        print(f"响应内容: {response.text}")
        return
    
    # 2. 测试用户登录
    print("\n2. 测试用户登录...")
    login_data = {
        "username": username,
        "password": password
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/login/", json=login_data)
    print(f"登录响应状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            print("✅ 登录成功!")
            new_access_token = result['data']['token']['access_token']
            new_refresh_token = result['data']['token']['refresh_token']
            print(f"新的Access Token: {new_access_token[:30]}...")
        else:
            print(f"❌ 登录失败: {result.get('message', '未知错误')}")
            return
    else:
        print(f"❌ 登录失败: {response.status_code}")
        print(f"响应内容: {response.text}")
        return
    
    # 3. 测试获取用户资料
    print("\n3. 测试获取用户资料...")
    headers = {
        'Authorization': f'Bearer {new_access_token}',
        'Content-Type': 'application/json'
    }
    
    response = requests.get(f"{BASE_URL}/api/auth/profile/", headers=headers)
    print(f"获取资料响应状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            print("✅ 获取用户资料成功!")
            print(f"用户信息: {json.dumps(result['data'], ensure_ascii=False, indent=2)}")
        else:
            print(f"❌ 获取用户资料失败: {result.get('message', '未知错误')}")
    else:
        print(f"❌ 获取用户资料失败: {response.status_code}")
        print(f"响应内容: {response.text}")
    
    # 4. 测试更新用户资料
    print("\n4. 测试更新用户资料...")
    update_data = {
        "nickname": "更新后的昵称",
        "phone": "13900139000"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/profile/update/", json=update_data, headers=headers)
    print(f"更新资料响应状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            print("✅ 更新用户资料成功!")
            print(f"更新后的用户信息: {json.dumps(result['data'], ensure_ascii=False, indent=2)}")
        else:
            print(f"❌ 更新用户资料失败: {result.get('message', '未知错误')}")
    else:
        print(f"❌ 更新用户资料失败: {response.status_code}")
        print(f"响应内容: {response.text}")
    
    # 5. 测试刷新Token
    print("\n5. 测试刷新Token...")
    refresh_headers = {
        'Authorization': f'Bearer {new_refresh_token}',
        'Content-Type': 'application/json'
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/refresh/", headers=refresh_headers)
    print(f"刷新Token响应状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            print("✅ 刷新Token成功!")
            refreshed_access_token = result['data']['access_token']
            print(f"新的Access Token: {refreshed_access_token[:30]}...")
        else:
            print(f"❌ 刷新Token失败: {result.get('message', '未知错误')}")
    else:
        print(f"❌ 刷新Token失败: {response.status_code}")
        print(f"响应内容: {response.text}")
    
    # 6. 测试退出登录
    print("\n6. 测试退出登录...")
    response = requests.post(f"{BASE_URL}/api/auth/logout/", headers=headers)
    print(f"退出登录响应状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            print("✅ 退出登录成功!")
            print(f"消息: {result.get('message', '未知')}")
        else:
            print(f"❌ 退出登录失败: {result.get('message', '未知错误')}")
    else:
        print(f"❌ 退出登录失败: {response.status_code}")
        print(f"响应内容: {response.text}")
    
    # 7. 测试无token访问受保护API
    print("\n7. 测试无token访问受保护API...")
    response = requests.get(f"{BASE_URL}/api/auth/profile/")
    print(f"无token访问响应状态码: {response.status_code}")
    
    if response.status_code == 401:
        print("✅ 无token访问被正确拒绝")
    else:
        print(f"❌ 无token访问没有被正确拒绝: {response.status_code}")
    
    print("\n=== 所有认证API测试完成 ===")

if __name__ == "__main__":
    test_all_auth_apis() 