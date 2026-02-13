#!/usr/bin/env python3
"""测试search-by-name API"""

import requests

url = "http://localhost:8000/api/retirement/search-by-name?name=王军峰"

try:
    response = requests.get(url)
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {data}")
    
    if data.get('status') == 'success' and data.get('data'):
        teachers = data['data']
        print(f"\n找到 {len(teachers)} 个教师:")
        for teacher in teachers:
            print(f"  ID: {teacher.get('id')}, 姓名: {teacher.get('teacher_name')}")
    else:
        print("没有找到教师")
except Exception as e:
    print(f"Error: {e}")
