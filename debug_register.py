import requests
import json

# 测试注册
url = "http://localhost:8000/api/auth/register/"
data = {
    "username": "testuser5",
    "password": "123456",
    "confirm_password": "123456",
    "nickname": "测试用户5",
    "phone": "13800138003"
}

print("发送数据:", json.dumps(data, indent=2, ensure_ascii=False))
print("URL:", url)

try:
    response = requests.post(url, json=data)
    print(f"状态码: {response.status_code}")
    print(f"响应头: {dict(response.headers)}")
    print(f"响应内容: {response.text}")
    
    if response.status_code == 200:
        print("✅ 注册成功!")
    else:
        print("❌ 注册失败!")
        
except Exception as e:
    print(f"请求异常: {e}") 