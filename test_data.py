#!/usr/bin/env python3
"""测试数据加载"""
import requests

response = requests.get("http://localhost:8000/api/auto-table/retirement_report_data/list?page=1&page_size=10")
print(f"状态码: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    print(f"状态: {data.get('status')}")
    print(f"总记录数: {data.get('total')}")
    print(f"返回记录数: {len(data.get('data', []))}")
    
    if data.get('data'):
        print("\n第一条记录:")
        print(data['data'][0])
    else:
        print("\n没有数据返回")
else:
    print(f"错误: {response.text}")
