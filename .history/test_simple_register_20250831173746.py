import requests
import json

# 测试简化注册
url = "http://localhost:8000/api/auth/register/"
data = {
    "username": "testuser6",
    "password": "123456",
    "nickname": "测试用户6"
}

print("发送简化数据:", json.dumps(data, indent=2, ensure_ascii=False))
print("URL:", url)

try:
    response = requests.post(url, json=data)
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {response.text}")
    
    if response.status_code == 200:
        print("✅ 简化注册成功!")
    else:
        print("❌ 简化注册失败!")
        
except Exception as e:
    print(f"请求异常: {e}")

# 测试登录
print("\n=== 测试登录 ===")
login_url = "http://localhost:8000/api/auth/login/"
login_data = {
    "username_or_phone": "testuser6",
    "password": "123456"
}

print("登录数据:", json.dumps(login_data, indent=2, ensure_ascii=False))

try:
    login_response = requests.post(login_url, json=login_data)
    print(f"登录状态码: {login_response.status_code}")
    print(f"登录响应: {login_response.text}")
    
    if login_response.status_code == 200:
        print("✅ 登录成功!")
    else:
        print("❌ 登录失败!")
        
except Exception as e:
    print(f"登录异常: {e}") 