import requests
import json

# API基础URL
BASE_URL = 'http://localhost:8000/api'

def test_account_info_with_auth():
    """测试带认证的账户信息API"""
    print("=== 测试账户信息API ===")
    
    # 1. 先注册一个用户获取token
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
    
    # 2. 使用token获取账户信息
    print("\n2. 获取账户信息...")
    headers = {'Authorization': f'Bearer {access_token}'}
    
    account_response = requests.get(f"{BASE_URL}/account-info/", headers=headers)
    print(f"状态码: {account_response.status_code}")
    
    if account_response.status_code == 200:
        print("✅ 获取账户信息成功!")
        account_data = account_response.json()
        print(f"数据来源: {account_data.get('source', '未知')}")
        print(f"数据可用: {account_data.get('data_available', False)}")
        print(f"账户数量: {len(account_data.get('accounts', []))}")
        
        # 显示第一个账户的基本信息
        if account_data.get('accounts'):
            first_account = account_data['accounts'][0]
            print(f"账户ID: {first_account.get('account_id')}")
            print(f"总资产: {first_account.get('total_asset')}")
            print(f"持仓数量: {len(first_account.get('positions', []))}")
    else:
        print(f"❌ 获取账户信息失败: {account_response.text}")
    
    # 3. 测试资产类别API
    print("\n3. 获取资产类别分布...")
    category_response = requests.get(f"{BASE_URL}/asset-category/", headers=headers)
    print(f"状态码: {category_response.status_code}")
    
    if category_response.status_code == 200:
        print("✅ 获取资产类别成功!")
        category_data = category_response.json()
        print(f"数据可用: {category_data.get('data_available', False)}")
        print(f"类别数量: {len(category_data.get('categoryData', []))}")
    else:
        print(f"❌ 获取资产类别失败: {category_response.text}")

if __name__ == "__main__":
    test_account_info_with_auth() 