import requests
import json

def test_chart_apis():
    base_url = "http://localhost:8000"
    
    # 测试年度对比API
    print("=== 测试年度对比API ===")
    try:
        response = requests.get(f"{base_url}/api/timecomparison/yearly_comparison/")
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"返回数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
            # 检查是否包含真实数据标记
            if 'data_available' in data:
                print(f"数据可用性: {data['data_available']}")
        else:
            print(f"错误响应: {response.text}")
    except Exception as e:
        print(f"请求失败: {e}")
    
    print("\n=== 测试周度对比API ===")
    try:
        response = requests.get(f"{base_url}/api/timecomparison/weekly_comparison/")
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"返回数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
            if 'data_available' in data:
                print(f"数据可用性: {data['data_available']}")
        else:
            print(f"错误响应: {response.text}")
    except Exception as e:
        print(f"请求失败: {e}")
    
    print("\n=== 测试地区对比API ===")
    try:
        response = requests.get(f"{base_url}/api/areacomparsion/area_comparison/")
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"返回数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
            if 'data_available' in data:
                print(f"数据可用性: {data['data_available']}")
        else:
            print(f"错误响应: {response.text}")
    except Exception as e:
        print(f"请求失败: {e}")
    
    print("\n=== 测试资产分类API ===")
    try:
        response = requests.get(f"{base_url}/api/asset-category/")
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"返回数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
            if 'data_available' in data:
                print(f"数据可用性: {data['data_available']}")
        else:
            print(f"错误响应: {response.text}")
    except Exception as e:
        print(f"请求失败: {e}")

if __name__ == "__main__":
    test_chart_apis() 