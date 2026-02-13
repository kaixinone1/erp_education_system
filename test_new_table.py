#!/usr/bin/env python3
"""测试新表API"""
import requests

# 测试schema
print("=" * 50)
print("测试表结构API:")
print("=" * 50)
response = requests.get("http://localhost:8000/api/auto-table/teacher_training_records/schema")
print(f"状态码: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    if data.get('status') == 'success':
        fields = data['data'].get('fields', [])
        print(f"字段数量: {len(fields)}")
        for f in fields:
            print(f"  - {f['name']}")

# 测试数据列表
print("\n" + "=" * 50)
print("测试数据列表API:")
print("=" * 50)
response = requests.get("http://localhost:8000/api/auto-table/teacher_training_records/list?page=1&page_size=10")
print(f"状态码: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"状态: {data.get('status')}")
    print(f"总记录数: {data.get('total')}")
    print(f"返回记录数: {len(data.get('data', []))}")
    if data.get('data'):
        print("\n第一条记录:")
        print(data['data'][0])
