#!/usr/bin/env python3
"""
简单的认证测试脚本
"""

import requests
import json

# API基础URL
BASE_URL = 'http://localhost:8000/api'

def test_register_and_login():
    """测试注册和登录"""
    print("=== 测试注册和登录 ===")
    
    # 1. 注册
    register_data = {
        "username": "testuser2",
        "password": "123456",
        "confirm_password": "123456",
        "nickname": "测试用户2",
        "phone": "13800138001"
    }
    
    register_response = requests.post(f"{BASE_URL}/auth/register/", json=register_data)
    print(f"注册状态码: {register_response.status_code}")
    
    if register_response.status_code == 200:
        register_result = register_response.json()
        print("注册成功!")
        access_token = register_result['data']['token']['access_token']
        print(f"Access Token: {access_token[:50]}...")
        
        # 2. 测试获取用户资料
        headers = {'Authorization': f'Bearer {access_token}'}
        profile_response = requests.get(f"{BASE_URL}/auth/profile/", headers=headers)
        print(f"获取用户资料状态码: {profile_response.status_code}")
        
        if profile_response.status_code == 200:
            print("获取用户资料成功!")
            print(f"用户资料: {profile_response.json()}")
        else:
            print(f"获取用户资料失败: {profile_response.text}")
        
        # 3. 测试获取账户信息
        account_response = requests.get(f"{BASE_URL}/account-info/", headers=headers)
        print(f"获取账户信息状态码: {account_response.status_code}")
        
        if account_response.status_code == 200:
            print("获取账户信息成功!")
        else:
            print(f"获取账户信息失败: {account_response.text}")
    else:
        print(f"注册失败: {register_response.text}")

if __name__ == "__main__":
    test_register_and_login() 