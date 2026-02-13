#!/usr/bin/env python3
"""测试待办列表API"""

import requests

url = "http://localhost:8000/api/todo-work/list"

try:
    response = requests.get(url)
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {data}")
    
    if data.get('status') == 'success' and data.get('data'):
        first_item = data['data'][0]
        print(f"\n第一条数据:")
        print(f"  id: {first_item.get('id')}")
        print(f"  teacher_id: {first_item.get('teacher_id')}")
        print(f"  teacher_name: {first_item.get('teacher_name')}")
        print(f"  checklist_name: {first_item.get('checklist_name')}")
except Exception as e:
    print(f"Error: {e}")
