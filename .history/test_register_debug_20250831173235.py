#!/usr/bin/env python3
"""
调试注册API的测试脚本
"""

import requests
import json

# API基础URL
BASE_URL = 'http://localhost:8000/api'

def test_register_with_debug():
    """测试注册并显示详细信息"""
    print("=== 测试注册API ===")
    
    # 测试数据
    register_data = {
        "username": "testuser3",
        "password": "123456",
        "confirm_password": "123456",
        "nickname": "测试用户3",
        "phone": "13800138002"
    }
    
    print(f"发送数据: {json.dumps(register_data, indent=2, ensure_ascii=False)}")
    
    try:
        # 发送注册请求
        response = requests.post(f"{BASE_URL}/auth/register/", json=register_data)
        
        print(f"状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ 注册成功!")
            print(f"响应内容: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ 注册失败!")
            print(f"响应内容: {response.text}")
            
            # 尝试解析JSON错误信息
            try:
                error_data = response.json()
                print(f"错误详情: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print("无法解析错误响应为JSON")
                
    except requests.exceptions.ConnectionError:
        print("❌ 连接错误: 无法连接到服务器")
    except Exception as e:
        print(f"❌ 请求异常: {str(e)}")

def test_register_minimal():
    """测试最小化注册数据"""
    print("\n=== 测试最小化注册数据 ===")
    
    # 最小化数据
    minimal_data = {
        "username": "testuser4",
        "password": "123456",
        "confirm_password": "123456"
    }
    
    print(f"发送最小化数据: {json.dumps(minimal_data, indent=2, ensure_ascii=False)}")
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register/", json=minimal_data)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ 最小化注册成功!")
        else:
            print(f"❌ 最小化注册失败: {response.text}")
            
    except Exception as e:
        print(f"❌ 请求异常: {str(e)}")

if __name__ == "__main__":
    # 等待服务器启动
    import time
    print("等待服务器启动...")
    time.sleep(3)
    
    test_register_with_debug()
    test_register_minimal() 