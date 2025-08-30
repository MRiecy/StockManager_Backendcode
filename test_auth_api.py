#!/usr/bin/env python3
"""
认证API测试脚本
用于测试用户认证相关的API接口
"""

import requests
import json
import time

# API基础配置
BASE_URL = 'http://localhost:8000/api'
HEADERS = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

def test_send_verification_code():
    """测试发送验证码"""
    print("=== 测试发送验证码 ===")
    
    url = f"{BASE_URL}/auth/send-code/"
    data = {
        "phone": "13888888888"
    }
    
    try:
        response = requests.post(url, json=data, headers=HEADERS)
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200:
            print("✅ 发送验证码成功")
            return True
        else:
            print("❌ 发送验证码失败")
            return False
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return False

def test_login_with_phone():
    """测试手机号登录"""
    print("\n=== 测试手机号登录 ===")
    
    url = f"{BASE_URL}/auth/login/"
    data = {
        "phone": "13888888888",
        "code": "123456"  # 使用模拟验证码
    }
    
    try:
        response = requests.post(url, json=data, headers=HEADERS)
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ 登录成功")
                # 保存token用于后续测试
                global access_token, refresh_token
                access_token = result['data']['token']['access_token']
                refresh_token = result['data']['token']['refresh_token']
                return True
            else:
                print("❌ 登录失败")
                return False
        else:
            print("❌ 登录请求失败")
            return False
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return False

def test_get_current_user():
    """测试获取当前用户信息"""
    print("\n=== 测试获取当前用户信息 ===")
    
    if not access_token:
        print("❌ 缺少access_token")
        return False
    
    url = f"{BASE_URL}/auth/profile/"
    headers = HEADERS.copy()
    headers['Authorization'] = f'Bearer {access_token}'
    
    try:
        response = requests.get(url, headers=headers)
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ 获取用户信息成功")
                return True
            else:
                print("❌ 获取用户信息失败")
                return False
        else:
            print("❌ 获取用户信息请求失败")
            return False
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return False

def test_refresh_token():
    """测试刷新token"""
    print("\n=== 测试刷新token ===")
    
    if not refresh_token:
        print("❌ 缺少refresh_token")
        return False
    
    url = f"{BASE_URL}/auth/refresh/"
    headers = HEADERS.copy()
    headers['Authorization'] = f'Bearer {refresh_token}'
    
    try:
        response = requests.post(url, headers=headers)
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ 刷新token成功")
                # 更新access_token
                global access_token
                access_token = result['data']['access_token']
                return True
            else:
                print("❌ 刷新token失败")
                return False
        else:
            print("❌ 刷新token请求失败")
            return False
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return False

def test_logout():
    """测试退出登录"""
    print("\n=== 测试退出登录 ===")
    
    if not access_token:
        print("❌ 缺少access_token")
        return False
    
    url = f"{BASE_URL}/auth/logout/"
    headers = HEADERS.copy()
    headers['Authorization'] = f'Bearer {access_token}'
    
    try:
        response = requests.post(url, headers=headers)
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ 退出登录成功")
                return True
            else:
                print("❌ 退出登录失败")
                return False
        else:
            print("❌ 退出登录请求失败")
            return False
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return False

def test_account_info():
    """测试获取账户信息"""
    print("\n=== 测试获取账户信息 ===")
    
    if not access_token:
        print("❌ 缺少access_token")
        return False
    
    url = f"{BASE_URL}/account-info/"
    headers = HEADERS.copy()
    headers['Authorization'] = f'Bearer {access_token}'
    
    try:
        response = requests.get(url, headers=headers)
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200:
            print("✅ 获取账户信息成功")
            return True
        else:
            print("❌ 获取账户信息失败")
            return False
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始测试认证API接口")
    print("=" * 50)
    
    # 全局变量
    global access_token, refresh_token
    access_token = None
    refresh_token = None
    
    # 测试流程
    tests = [
        ("发送验证码", test_send_verification_code),
        ("手机号登录", test_login_with_phone),
        ("获取用户信息", test_get_current_user),
        ("刷新token", test_refresh_token),
        ("获取账户信息", test_account_info),
        ("退出登录", test_logout),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            print("-" * 30)
        except Exception as e:
            print(f"❌ {test_name}测试异常: {e}")
            print("-" * 30)
    
    print("=" * 50)
    print(f"🎯 测试完成: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！")
    else:
        print("⚠️  部分测试失败，请检查API实现")

if __name__ == "__main__":
    main() 