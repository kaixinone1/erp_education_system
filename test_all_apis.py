#!/usr/bin/env python3
"""测试所有相关API"""
import requests
from urllib.parse import quote

base_url = "http://localhost:8000"

print("=" * 70)
print("测试 API")
print("=" * 70)

# 1. 测试获取模板信息
print("\n1. 获取模板信息")
template_id = "职工退休呈报表html"
encoded_id = quote(template_id)
response = requests.get(f"{base_url}/api/templates/{encoded_id}")
print(f"   URL: /api/templates/{encoded_id}")
print(f"   状态: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"   模板名称: {data.get('template_name')}")
else:
    print(f"   错误: {response.text[:100]}")

# 2. 测试获取模板内容
print("\n2. 获取模板内容")
response = requests.get(f"{base_url}/api/templates/{encoded_id}/content")
print(f"   URL: /api/templates/{encoded_id}/content")
print(f"   状态: {response.status_code}")
if response.status_code == 200:
    print(f"   内容长度: {len(response.text)} 字符")
else:
    print(f"   错误: {response.text[:100]}")

# 3. 测试获取中间表数据
print("\n3. 获取中间表数据")
response = requests.get(f"{base_url}/api/auto-table/retirement_report_data/detail/273")
print(f"   URL: /api/auto-table/retirement_report_data/detail/273")
print(f"   状态: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    if data.get('status') == 'success':
        teacher_name = data.get('data', {}).get('姓名', '无')
        print(f"   教师姓名: {teacher_name}")
    else:
        print(f"   错误: {data}")
else:
    print(f"   错误: {response.text[:100]}")

print("\n" + "=" * 70)
print("测试完成!")
print("=" * 70)
