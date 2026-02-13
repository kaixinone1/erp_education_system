#!/usr/bin/env python3
"""测试字段提取API"""
import requests

template_id = "test_template_1770691934"
url = f"http://localhost:8000/api/templates/{template_id}/a3-regions/extract"

# 测试数据
data = {
    "page": 1,
    "regions": [
        {
            "id": 1,
            "bounds": {"x0": 85, "y0": 85, "x1": 585.3, "y1": 756.9}
        },
        {
            "id": 2,
            "bounds": {"x0": 605.3, "y0": 85, "x1": 1105.5, "y1": 756.9}
        }
    ]
}

print("请求数据:")
print(data)
print("\n发送请求...")

try:
    response = requests.post(url, json=data)
    print(f"\n状态码: {response.status_code}")
    print(f"响应: {response.text[:500]}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n状态: {result.get('status')}")
        print(f"字段数量: {result.get('fields_count')}")
        if result.get('fields'):
            print(f"\n前3个字段:")
            for f in result['fields'][:3]:
                print(f"  - {f.get('name')}: {f.get('label')}")
except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()
