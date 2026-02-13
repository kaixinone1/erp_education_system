#!/usr/bin/env python3
"""调试ReportView的模板加载"""
import requests
from urllib.parse import quote

# 测试几种不同的templateId格式
test_cases = [
    "职工退休呈报表html",  # 正确的template_id
    "职工退休申报表html",  # 错误的（申报vs呈报）
    "职工退休呈报表.html", # 带点的文件名
]

print("=" * 70)
print("测试ReportView模板加载")
print("=" * 70)

for template_id in test_cases:
    print(f"\n测试: {template_id}")
    encoded = quote(template_id)
    print(f"  URL编码: {encoded}")
    
    # 测试获取模板信息
    response = requests.get(f"http://localhost:8000/api/templates/{encoded}")
    print(f"  状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"  ✓ 找到模板: {data.get('template_name')}")
    else:
        print(f"  ✗ 模板不存在")

# 测试通过名称查找
print("\n" + "=" * 70)
print("测试通过名称查找（备用方案）")
print("=" * 70)

template_name = "职工退休呈报表.html"
encoded_name = quote(template_name)
response = requests.get(f"http://localhost:8000/api/templates/by-name/{encoded_name}")
print(f"\n查找: {template_name}")
print(f"  状态码: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    print(f"  ✓ 找到模板ID: {data.get('template_id')}")
