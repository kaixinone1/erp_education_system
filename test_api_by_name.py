#!/usr/bin/env python3
"""测试通过名称查找模板API"""
import requests
from urllib.parse import quote

# 测试通过模板名称查找
template_name = "职工退休呈报表.html"
encoded_name = quote(template_name)

print("=" * 60)
print(f"测试通过名称查找模板: {template_name}")
print("=" * 60)

response = requests.get(f"http://localhost:8000/api/templates/by-name/{encoded_name}")
print(f"状态码: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    print(f"\n找到模板:")
    print(f"  template_id: {data.get('template_id')}")
    print(f"  template_name: {data.get('template_name')}")
    print(f"  file_name: {data.get('file_name')}")
else:
    print(f"错误: {response.text}")

# 测试模糊匹配
print("\n" + "=" * 60)
print("测试模糊匹配: 退休呈报")
print("=" * 60)

response = requests.get(f"http://localhost:8000/api/templates/by-name/{quote('退休呈报')}")
print(f"状态码: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    print(f"\n找到模板:")
    print(f"  template_id: {data.get('template_id')}")
    print(f"  template_name: {data.get('template_name')}")
else:
    print(f"错误: {response.text}")
