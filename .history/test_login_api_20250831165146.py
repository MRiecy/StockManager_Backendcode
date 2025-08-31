#!/usr/bin/env python3
"""
测试登录API的脚本
"""

import requests
import json
import time

# API基础URL
BASE_URL = 'http://localhost:8000/api'

def test_send_verification_code():
    """测试发送验证码"""
    print("=== 测试发送验证码 ===")
    
    url = f"{BASE_URL}/auth/send-code/"
    data = {
        "phone": "13800138000"
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"错误: {e}")
        return False

def get_verification_code_from_db():
    """从数据库获取验证码（仅用于测试）"""
    try:
        # 这里我们直接使用一个已知的验证码进行测试
        # 在实际环境中，验证码应该通过短信发送
        return "123456"
    except:
        return "123456"

def test_login():
    """测试登录"""
    print("\n=== 测试登录 ===")
    
    # 先发送验证码
    test_send_verification_code()
    
    # 等待一秒让验证码保存到数据库
    time.sleep(1)
    
    url = f"{BASE_URL}/auth/login/"
    data = {
        "phone": "13800138000",
        "code": "123456"  # 使用模拟验证码
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
    """测试获取账户信息"""
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

def main():
    """主测试函数"""
    print("开始测试登录API...")
    
    # 测试发送验证码
    send_code_success = test_send_verification_code()
    
    # 测试登录
    access_token = test_login()
    
    if access_token:
        # 测试获取用户资料
        test_get_profile(access_token)
        
        # 测试刷新token
        test_refresh_token(access_token)
        
        # 测试退出登录
        test_logout(access_token)
    
    # 测试获取账户信息
    test_account_info()
    
    print("\n测试完成!")

if __name__ == "__main__":
    main() 