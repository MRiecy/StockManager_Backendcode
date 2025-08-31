#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试注册API的错误
"""

import requests
import json

def test_register_api():
    """测试注册API"""
    url = "http://127.0.0.1:8000/api/auth/register/"
    
    # 测试数据
    data = {
        "username": "testuser123",
        "password": "testpass123",
        "nickname": "测试用户",
        "phone": "13800138000"
    }
    
    print(f"测试URL: {url}")
    print(f"测试数据: {json.dumps(data, ensure_ascii=False)}")
    
    try:
        response = requests.post(url, json=data)
        print(f"响应状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"注册成功: {json.dumps(result, ensure_ascii=False, indent=2)}")
        else:
            print(f"注册失败: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 连接失败 - Django服务器可能没有运行")
    except Exception as e:
        print(f"❌ 请求异常: {e}")

if __name__ == "__main__":
    test_register_api() 