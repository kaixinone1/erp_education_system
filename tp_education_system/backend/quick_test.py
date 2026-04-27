#!/usr/bin/env python3
import requests

try:
    response = requests.get('http://127.0.0.1:8000/api/todo-system/todo-list', timeout=10)
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        data = result.get('data', [])
        print(f"数据条数: {len(data)}")
        for item in data[:3]:
            print(f"\n{item.get('teacher_name')}:")
            print(f"  title: {item.get('title')}")
            print(f"  business_type_display: {item.get('business_type_display')}")
except Exception as e:
    print(f"错误: {e}")
