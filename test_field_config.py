#!/usr/bin/env python3
"""测试字段配置 API"""
import requests

# 测试获取教师基础信息的字段配置
table_name = 'teacher_basic_info'
url = f'http://127.0.0.1:8000/api/table-structure/{table_name}/field-config'

print(f"测试获取字段配置: {url}")
response = requests.get(url)
print(f"状态码: {response.status_code}")
print(f"响应: {response.text}")
