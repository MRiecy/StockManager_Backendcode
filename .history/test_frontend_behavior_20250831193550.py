#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模拟前端行为，测试token管理和状态
"""

import requests
import json
import time

# API基础URL
BASE_URL = "http://127.0.0.1:8000"

def test_frontend_behavior():
    """模拟前端行为"""
    print("=== 模拟前端行为测试 ===")
    
    # 模拟前端的token存储
    frontend_tokens = {
        'access_token': None,
        'refresh_token': None,
        'user_info': None
    }
    
    # 生成唯一用户名
    timestamp = int(time.time())
    username = f"frontenduser{timestamp}"
    password = "testpass123"
    
    print(f"测试用户名: {username}")
    print(f"测试密码: {password}")
    
    # 1. 注册用户
    print("\n1. 前端注册用户...")
    register_data = {
        "username": username,
        "password": password,
        "nickname": "前端测试用户",
        "phone": "13400134000"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/register/", json=register_data)
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            print("✅ 注册成功!")
            # 模拟前端保存用户信息
            frontend_tokens['user_info'] = result['data']['user']
        else:
            print(f"❌ 注册失败: {result.get('message', '未知错误')}")
            return
    else:
        print(f"❌ 注册请求失败: {response.status_code}")
        return
    
    # 2. 前端登录
    print("\n2. 前端登录...")
    login_data = {
        "username": username,
        "password": password
    }
    
    print(f"前端发送登录数据: {json.dumps(login_data, ensure_ascii=False)}")
    
    response = requests.post(f"{BASE_URL}/api/auth/login/", json=login_data)
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            print("✅ 前端登录成功!")
            # 模拟前端保存token
            frontend_tokens['access_token'] = result['data']['token']['access_token']
            frontend_tokens['refresh_token'] = result['data']['token']['refresh_token']
            print(f"前端保存的access_token: {frontend_tokens['access_token'][:30]}...")
        else:
            print(f"❌ 前端登录失败: {result.get('message', '未知错误')}")
            return
    else:
        print(f"❌ 前端登录失败: {response.status_code}")
        print(f"响应内容: {response.text}")
        return
    
    # 3. 前端使用token访问受保护的API
    print("\n3. 前端使用token访问受保护的API...")
    headers = {
        'Authorization': f'Bearer {frontend_tokens["access_token"]}',
        'Content-Type': 'application/json'
    }
    
    response = requests.get(f"{BASE_URL}/api/auth/profile/", headers=headers)
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            print("✅ 前端成功访问受保护API!")
            print(f"用户信息: {json.dumps(result['data'], ensure_ascii=False, indent=2)}")
        else:
            print(f"❌ 前端访问受保护API失败: {result.get('message', '未知错误')}")
    else:
        print(f"❌ 前端访问受保护API失败: {response.status_code}")
        print(f"响应内容: {response.text}")
    
    # 4. 前端退出登录
    print("\n4. 前端退出登录...")
    response = requests.post(f"{BASE_URL}/api/auth/logout/", headers=headers)
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            print("✅ 前端退出登录成功!")
            # 模拟前端清除token
            frontend_tokens['access_token'] = None
            frontend_tokens['refresh_token'] = None
            print("前端已清除token")
        else:
            print(f"❌ 前端退出登录失败: {result.get('message', '未知错误')}")
    else:
        print(f"❌ 前端退出登录失败: {response.status_code}")
        print(f"响应内容: {response.text}")
    
    # 5. 前端尝试重新登录（关键测试）
    print("\n5. 前端尝试重新登录...")
    print(f"前端发送登录数据: {json.dumps(login_data, ensure_ascii=False)}")
    
    response = requests.post(f"{BASE_URL}/api/auth/login/", json=login_data)
    print(f"重新登录响应状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            print("✅ 前端重新登录成功!")
            # 模拟前端重新保存token
            frontend_tokens['access_token'] = result['data']['token']['access_token']
            frontend_tokens['refresh_token'] = result['data']['token']['refresh_token']
            print(f"前端重新保存的access_token: {frontend_tokens['access_token'][:30]}...")
        else:
            print(f"❌ 前端重新登录失败: {result.get('message', '未知错误')}")
            print(f"错误详情: {result.get('errors', '无')}")
    else:
        print(f"❌ 前端重新登录失败: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        # 分析错误原因
        if response.status_code == 400:
            try:
                error_result = response.json()
                print(f"错误详情: {json.dumps(error_result, ensure_ascii=False, indent=2)}")
            except:
                print(f"原始错误内容: {response.text}")
    
    # 6. 测试前端可能的问题场景
    print("\n6. 测试前端可能的问题场景...")
    
    # 场景1：前端发送空数据
    print("\n场景1：前端发送空数据")
    empty_data = {}
    response = requests.post(f"{BASE_URL}/api/auth/login/", json=empty_data)
    print(f"空数据登录响应状态码: {response.status_code}")
    if response.status_code == 400:
        result = response.json()
        print(f"✅ 空数据被正确拒绝: {result.get('message', '未知错误')}")
        print(f"错误详情: {result.get('errors', '无')}")
    
    # 场景2：前端发送缺少密码的数据
    print("\n场景2：前端发送缺少密码的数据")
    no_password_data = {"username": username}
    response = requests.post(f"{BASE_URL}/api/auth/login/", json=no_password_data)
    print(f"缺少密码登录响应状态码: {response.status_code}")
    if response.status_code == 400:
        result = response.json()
        print(f"✅ 缺少密码被正确拒绝: {result.get('message', '未知错误')}")
        print(f"错误详情: {result.get('errors', '无')}")
    
    # 场景3：前端发送错误Content-Type
    print("\n场景3：前端发送错误Content-Type")
    wrong_headers = {'Content-Type': 'text/plain'}
    response = requests.post(f"{BASE_URL}/api/auth/login/", data=json.dumps(login_data), headers=wrong_headers)
    print(f"错误Content-Type登录响应状态码: {response.status_code}")
    print(f"响应内容: {response.text}")
    
    # 场景4：前端发送form-data格式
    print("\n场景4：前端发送form-data格式")
    response = requests.post(f"{BASE_URL}/api/auth/login/", data=login_data)
    print(f"form-data格式登录响应状态码: {response.status_code}")
    if response.status_code == 400:
        result = response.json()
        print(f"✅ form-data格式被正确处理: {result.get('message', '未知错误')}")
    
    print("\n=== 前端行为测试完成 ===")

if __name__ == "__main__":
    test_frontend_behavior() 