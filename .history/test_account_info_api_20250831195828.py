#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试account-info API是否正常工作
"""

import requests
import json
import time

# API基础URL
BASE_URL = "http://127.0.0.1:8000"

def test_account_info_api():
    """测试account-info API"""
    print("=== 测试account-info API ===")
    
    # 生成唯一用户名
    timestamp = int(time.time())
    username = f"apitest{timestamp}"
    password = "testpass123"
    
    print(f"测试用户名: {username}")
    print(f"测试密码: {password}")
    
    # 1. 注册用户
    print("\n1. 注册用户...")
    register_data = {
        "username": username,
        "password": password,
        "nickname": "API测试用户",
        "phone": "13300133000"
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
        "password": password
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/login/", json=login_data)
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            print("✅ 登录成功!")
            access_token = result['data']['token']['access_token']
            print(f"获取到access_token: {access_token[:30]}...")
        else:
            print(f"❌ 登录失败: {result.get('message', '未知错误')}")
            return
    else:
        print(f"❌ 登录失败: {response.status_code}")
        return
    
    # 3. 测试account-info API（关键测试）
    print("\n3. 测试account-info API...")
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    print(f"请求头: {json.dumps(headers, ensure_ascii=False)}")
    print(f"请求URL: {BASE_URL}/api/account-info/")
    
    response = requests.get(f"{BASE_URL}/api/account-info/", headers=headers)
    print(f"响应状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"响应数据: {json.dumps(result, ensure_ascii=False, indent=2)}")
        
        # 检查是否有accounts字段，这是成功的关键指标
        if 'accounts' in result:
            print("✅ account-info API调用成功!")
            print(f"账户数量: {len(result['accounts'])}")
            print(f"数据来源: {result.get('source', '未知')}")
            print(f"数据可用性: {result.get('data_available', '未知')}")
        else:
            print(f"❌ account-info API返回数据格式错误，缺少accounts字段")
    else:
        print(f"❌ account-info API调用失败: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        # 分析错误原因
        if response.status_code == 401:
            print("🔍 401错误分析:")
            print("- 可能是token无效或过期")
            print("- 可能是认证头格式错误")
            print("- 可能是后端认证配置问题")
        elif response.status_code == 500:
            print("🔍 500错误分析:")
            print("- 可能是后端服务器内部错误")
            print("- 可能是XtQuant连接问题")
            print("- 可能是数据库连接问题")
    
    # 4. 测试不带token的请求
    print("\n4. 测试不带token的请求...")
    response = requests.get(f"{BASE_URL}/api/account-info/")
    print(f"无token请求响应状态码: {response.status_code}")
    
    if response.status_code == 401:
        print("✅ 无token请求被正确拒绝")
    else:
        print(f"❌ 无token请求没有被正确拒绝: {response.status_code}")
    
    # 5. 测试错误的token格式
    print("\n5. 测试错误的token格式...")
    wrong_headers = {
        'Authorization': 'Bearer invalid_token_here',
        'Content-Type': 'application/json'
    }
    
    response = requests.get(f"{BASE_URL}/api/account-info/", headers=wrong_headers)
    print(f"错误token请求响应状态码: {response.status_code}")
    
    if response.status_code == 401:
        print("✅ 错误token被正确拒绝")
    else:
        print(f"❌ 错误token没有被正确拒绝: {response.status_code}")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_account_info_api() 