#!/usr/bin/env python3
"""测试模板API - 使用正确的模板ID"""
import requests

# 正确的模板ID
template_id = "职工退休申报表html"

# 测试获取单个模板
print("=" * 50)
print(f"测试获取单个模板: {template_id}")
print("=" * 50)
response = requests.get(f"http://localhost:8000/api/templates/{template_id}")
print(f"状态码: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"模板信息: {data}")
else:
    print(f"错误: {response.text}")

# 测试获取模板内容
print("\n" + "=" * 50)
print(f"测试获取模板内容: {template_id}")
print("=" * 50)
response = requests.get(f"http://localhost:8000/api/templates/{template_id}/content")
print(f"状态码: {response.status_code}")
if response.status_code == 200:
    print("内容长度:", len(response.text))
    print("内容前500字符:", response.text[:500])
else:
    print(f"错误: {response.text}")
