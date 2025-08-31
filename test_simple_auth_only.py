#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试认证系统 - 只测试核心认证功能
"""

import requests
import json
import time

# API基础URL
BASE_URL = "http://127.0.0.1:8000"

def test_auth_system():
    """测试认证系统"""
    print("=== 测试认证系统 ===")
    
    # 生成唯一用户名
    timestamp = int(time.time())
    username = f"testuser{timestamp}"
    
    # 1. 注册用户
    print("1. 注册用户...")
    register_data = {
        "username": username,
        "password": "testpass123",
        "nickname": "测试用户",
        "phone": "13800138000"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/register/", json=register_data)
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            print("✅ 注册成功!")
            access_token = result['data']['token']['access_token']
        else:
            print(f"❌ 注册失败: {result.get('message', '未知错误')}")
            return
    else:
        print(f"❌ 注册请求失败: {response.status_code}")
        return
    
    # 2. 获取用户资料
    print("2. 获取用户资料...")
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    response = requests.get(f"{BASE_URL}/api/auth/profile/", headers=headers)
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            print("✅ 获取用户资料成功!")
            profile_data = result['data']
            print(f"用户ID: {profile_data['id']}")
            print(f"用户名: {profile_data['username']}")
            print(f"邮箱: {profile_data['email']}")
            print(f"姓: {profile_data['first_name']}")
            print(f"名: {profile_data['last_name']}")
            print(f"注册时间: {profile_data['date_joined']}")
            print(f"最后登录: {profile_data['last_login']}")
            print(f"是否激活: {profile_data['is_active']}")
        else:
            print(f"❌ 获取用户资料失败: {result.get('message', '未知错误')}")
    else:
        print(f"❌ 获取用户资料请求失败: {response.status_code}")
        print(f"响应内容: {response.text}")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_auth_system() 