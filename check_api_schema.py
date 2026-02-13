#!/usr/bin/env python3
import requests

url = 'http://localhost:8000/api/data/schema/retirement_report_data'
print(f"请求: {url}")

try:
    response = requests.get(url)
    print(f"状态码: {response.status_code}")
    data = response.json()
    
    print(f"\n表中文名: {data.get('chinese_name')}")
    print(f"字段数: {len(data.get('fields', []))}")
    
    print("\n前10个字段:")
    for field in data.get('fields', [])[:10]:
        print(f"  name: {field.get('name')}")
        print(f"  label: {field.get('label')}")
        print(f"  source_name: {field.get('source_name')}")
        print(f"  ---")
except Exception as e:
    print(f"错误: {e}")
