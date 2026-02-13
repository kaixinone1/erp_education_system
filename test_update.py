#!/usr/bin/env python3
"""测试更新API"""
import requests

# 测试更新教师学历记录
url = 'http://127.0.0.1:8000/api/data/teacher_education_record/1'
data = {
    'education_type': '2',
    'education': '6'
}

response = requests.put(url, json=data)
print(f"状态码: {response.status_code}")
print(f"响应: {response.text}")
