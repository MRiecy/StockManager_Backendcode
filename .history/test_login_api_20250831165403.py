#!/usr/bin/env python3
"""
测试用户名密码登录API的脚本
"""

import requests
import json
import time

# API基础URL
BASE_URL = 'http://localhost:8000/api'

def test_register():
    """测试用户注册"""
    print("=== 测试用户注册 ===")
    
    url = f"{BASE_URL}/auth/register/"
    data = {
        "username": "testuser",
        "password": "123456",
        "confirm_password": "123456",
        "nickname": "测试用户",
        "phone": "13800138000"
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                return result.get('data', {}).get('token', {}).get('access_token')
        return None
    except Exception as e:
        print(f"错误: {e}")
        return None

def test_login():
    """测试用户登录"""
    print("\n=== 测试用户登录 ===")
    
    url = f"{BASE_URL}/auth/login/"
    data = {
        "username": "testuser",
        "password": "123456"
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                return result.get('data', {}).get('token', {}).get('access_token')
        return None
    except Exception as e:
        print(f"错误: {e}")
        return None

def test_get_profile(access_token):
    """测试获取用户资料"""
    print("\n=== 测试获取用户资料 ===")
    
    url = f"{BASE_URL}/auth/profile/"
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    
    try:
        response = requests.get(url, headers=headers)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"错误: {e}")
        return False

def test_update_profile(access_token):
    """测试更新用户资料"""
    print("\n=== 测试更新用户资料 ===")
    
    url = f"{BASE_URL}/auth/profile/update/"
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    data = {
        "nickname": "更新后的昵称",
        "phone": "13900139000"
    }
    
    try:
        response = requests.post(url, json=data, headers=headers)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"错误: {e}")
        return False

def test_refresh_token(access_token):
    """测试刷新token"""
    print("\n=== 测试刷新Token ===")
    
    url = f"{BASE_URL}/auth/refresh/"
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    
    try:
        response = requests.post(url, headers=headers)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"错误: {e}")
        return False

def test_logout(access_token):
    """测试退出登录"""
    print("\n=== 测试退出登录 ===")
    
    url = f"{BASE_URL}/auth/logout/"
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    
    try:
        response = requests.post(url, headers=headers)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"错误: {e}")
        return False

def test_account_info():
    """测试获取账户信息（需要认证）"""
    print("\n=== 测试获取账户信息 ===")
    
    url = f"{BASE_URL}/account-info/"
    
    try:
        response = requests.get(url)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"错误: {e}")
        return False

def test_account_info_with_auth(access_token):
    """测试获取账户信息（带认证）"""
    print("\n=== 测试获取账户信息（带认证） ===")
    
    url = f"{BASE_URL}/account-info/"
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    
    try:
        response = requests.get(url, headers=headers)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"错误: {e}")
        return False

def main():
    """主测试函数"""
    print("开始测试用户名密码登录API...")
    
    # 测试注册
    register_token = test_register()
    
    # 测试登录
    login_token = test_login()
    
    # 使用登录获取的token进行后续测试
    access_token = login_token or register_token
    
    if access_token:
        # 测试获取用户资料
        test_get_profile(access_token)
        
        # 测试更新用户资料
        test_update_profile(access_token)
        
        # 测试刷新token
        test_refresh_token(access_token)
        
        # 测试获取账户信息（带认证）
        test_account_info_with_auth(access_token)
        
        # 测试退出登录
        test_logout(access_token)
    
    # 测试获取账户信息（无认证）
    test_account_info()
    
    print("\n测试完成!")

if __name__ == "__main__":
    main() 