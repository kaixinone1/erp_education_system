#!/usr/bin/env python3
"""测试API返回的字段顺序"""
import requests
import json

response = requests.get("http://localhost:8000/api/auto-table/retirement_report_data/schema")
if response.status_code == 200:
    data = response.json()
    if data.get('status') == 'success':
        fields = data['data'].get('fields', [])
        print(f"字段数量: {len(fields)}")
        print("\n字段顺序:")
        for i, field in enumerate(fields, 1):
            print(f"  {i}. {field['name']} -> {field.get('label', field['name'])}")
    else:
        print(f"API返回错误: {data}")
else:
    print(f"请求失败: {response.status_code}")
    print(response.text)
