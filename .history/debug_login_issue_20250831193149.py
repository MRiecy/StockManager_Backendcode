#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
诊断登录问题的根本原因
"""

import requests
import json
import time

# API基础URL
BASE_URL = "http://127.0.0.1:8000"

def debug_login_issue():
    """诊断登录问题"""
    print("=== 诊断登录问题 ===")
    
    # 生成唯一用户名
    timestamp = int(time.time())
    username = f"debuguser{timestamp}"
    password = "testpass123"
    
    print(f"测试用户名: {username}")
    print(f"测试密码: {password}")
    
    # 1. 注册用户
    print("\n1. 注册用户...")
    register_data = {
        "username": username,
        "password": password,
        "nickname": "诊断测试用户",
        "phone": "13500135000"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/register/", json=register_data)
    print(f"注册响应状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            print("✅ 注册成功!")
            print(f"用户ID: {result['data']['user']['id']}")
            print(f"用户名: {result['data']['user']['username']}")
        else:
            print(f"❌ 注册失败: {result.get('message', '未知错误')}")
            print(f"错误详情: {result.get('errors', '无')}")
            return
    else:
        print(f"❌ 注册请求失败: {response.status_code}")
        print(f"响应内容: {response.text}")
        return
    
    # 2. 第一次登录
    print("\n2. 第一次登录...")
    login_data = {
        "username": username,
        "password": password
    }
    
    print(f"发送登录数据: {json.dumps(login_data, ensure_ascii=False)}")
    
    response = requests.post(f"{BASE_URL}/api/auth/login/", json=login_data)
    print(f"第一次登录响应状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            print("✅ 第一次登录成功!")
            access_token = result['data']['token']['access_token']
            refresh_token = result['data']['token']['refresh_token']
            print(f"Access Token: {access_token[:30]}...")
            print(f"Refresh Token: {refresh_token[:30]}...")
        else:
            print(f"❌ 第一次登录失败: {result.get('message', '未知错误')}")
            return
    else:
        print(f"❌ 第一次登录失败: {response.status_code}")
        print(f"响应内容: {response.text}")
        return
    
    # 3. 获取用户资料（验证token）
    print("\n3. 获取用户资料（验证token）...")
    headers = {
        'Authorization': f'Bearer {access_token}',
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
    
    # 4. 退出登录
    print("\n4. 退出登录...")
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
    
    # 5. 尝试再次登录（关键测试）
    print("\n5. 尝试再次登录（关键测试）...")
    print(f"发送登录数据: {json.dumps(login_data, ensure_ascii=False)}")
    
    response = requests.post(f"{BASE_URL}/api/auth/login/", json=login_data)
    print(f"再次登录响应状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            print("✅ 再次登录成功!")
            new_access_token = result['data']['token']['access_token']
            print(f"新的Access Token: {new_access_token[:30]}...")
        else:
            print(f"❌ 再次登录失败: {result.get('message', '未知错误')}")
            print(f"错误详情: {result.get('errors', '无')}")
    else:
        print(f"❌ 再次登录失败: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        # 尝试分析错误原因
        if response.status_code == 400:
            try:
                error_result = response.json()
                print(f"错误详情: {json.dumps(error_result, ensure_ascii=False, indent=2)}")
            except:
                print(f"原始错误内容: {response.text}")
    
    # 6. 测试使用错误的用户名
    print("\n6. 测试使用错误的用户名...")
    wrong_login_data = {
        "username": f"wrong_{username}",
        "password": password
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/login/", json=wrong_login_data)
    print(f"错误用户名登录响应状态码: {response.status_code}")
    
    if response.status_code == 400:
        result = response.json()
        print(f"✅ 错误用户名被正确拒绝: {result.get('message', '未知错误')}")
    else:
        print(f"❌ 错误用户名没有被正确拒绝: {response.status_code}")
    
    # 7. 测试使用错误的密码
    print("\n7. 测试使用错误的密码...")
    wrong_password_data = {
        "username": username,
        "password": "wrongpassword"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/login/", json=wrong_password_data)
    print(f"错误密码登录响应状态码: {response.status_code}")
    
    if response.status_code == 400:
        result = response.json()
        print(f"✅ 错误密码被正确拒绝: {result.get('message', '未知错误')}")
    else:
        print(f"❌ 错误密码没有被正确拒绝: {response.status_code}")
    
    print("\n=== 诊断完成 ===")

if __name__ == "__main__":
    debug_login_issue() 