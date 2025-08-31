import requests
import json

# API基础URL
BASE_URL = 'http://localhost:8000/api'

def test_auth_only():
    """只测试认证，不测试账户信息API"""
    print("=== 测试认证系统 ===")
    
    # 1. 注册用户
    import time
    timestamp = int(time.time())
    register_data = {
        "username": f"testuser{timestamp}",
        "password": "123456",
        "nickname": f"测试用户{timestamp}"
    }
    
    print("1. 注册用户...")
    register_response = requests.post(f"{BASE_URL}/auth/register/", json=register_data)
    
    if register_response.status_code != 200:
        print(f"❌ 注册失败: {register_response.text}")
        return
    
    print("✅ 注册成功!")
    register_result = register_response.json()
    access_token = register_result['data']['token']['access_token']
    
    # 2. 测试获取用户资料（这个不需要XtQuant）
    print("\n2. 获取用户资料...")
    headers = {'Authorization': f'Bearer {access_token}'}
    
    profile_response = requests.get(f"{BASE_URL}/auth/profile/", headers=headers)
    print(f"状态码: {profile_response.status_code}")
    
    if profile_response.status_code == 200:
        print("✅ 获取用户资料成功!")
        profile_data = profile_response.json()
        print(f"用户名: {profile_data['data']['username']}")
        print(f"昵称: {profile_data['data']['nickname']}")
    else:
        print(f"❌ 获取用户资料失败: {profile_response.text}")
    
    print("\n✅ 认证系统测试完成！")
    print("问题可能出现在XtQuant连接上，而不是认证系统本身。")

if __name__ == "__main__":
    test_auth_only() 