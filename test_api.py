#!/usr/bin/env python3
"""测试API"""
import requests
from urllib.parse import quote

# 测试获取模板
print("=" * 60)
print("测试获取模板")
print("=" * 60)

template_id = "职工退休呈报表html"
encoded_id = quote(template_id)

print(f"\n1. 获取模板信息: {template_id}")
response = requests.get(f"http://localhost:8000/api/templates/{encoded_id}")
print(f"   状态码: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"   模板名称: {data.get('template_name')}")
else:
    print(f"   错误: {response.text[:100]}")

print(f"\n2. 获取模板内容")
response = requests.get(f"http://localhost:8000/api/templates/{encoded_id}/content")
print(f"   状态码: {response.status_code}")
if response.status_code == 200:
    print(f"   内容长度: {len(response.text)} 字符")
else:
    print(f"   错误: {response.text[:100]}")

# 测试中间表数据
print(f"\n3. 获取中间表数据")
response = requests.get(f"http://localhost:8000/api/auto-table/retirement_report_data/detail/273")
print(f"   状态码: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"   数据: {data.get('data', {}).get('姓名', '无')}")
else:
    print(f"   错误: {response.text[:100]}")
