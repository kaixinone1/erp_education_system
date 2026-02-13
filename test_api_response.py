#!/usr/bin/env python3
"""测试 API 返回的数据"""
import requests

# 测试获取退休呈报表详细数据
response = requests.get('http://localhost:8000/api/retirement/data/detail/273')
data = response.json()

print(f"状态码: {response.status_code}")
print(f"响应内容: {data}")

if data.get('status') == 'success' and 'data' in data:
    print("\nAPI 返回的字段：")
    for key, value in data['data'].items():
        print(f"  {key}: {value}")
    
    # 检查是否有个人身份字段
    if '个人身份' in data['data']:
        print(f"\n✓ 个人身份字段存在，值为: {data['data']['个人身份']}")
    else:
        print("\n✗ 个人身份字段不存在")
