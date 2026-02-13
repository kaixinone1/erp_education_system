#!/usr/bin/env python3
"""测试模板API"""
import requests
from urllib.parse import quote

# 测试通过名称查找
template_name = "职工退休呈报表.html"
encoded_name = quote(template_name)

print("=" * 60)
print(f"1. 通过名称查找模板: {template_name}")
print("=" * 60)

response = requests.get(f"http://localhost:8000/api/templates/by-name/{encoded_name}")
print(f"状态码: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    print(f"\n返回数据:")
    for key, value in data.items():
        print(f"  {key}: {value}")
    
    # 获取template_id
    template_id = data.get('template_id')
    print(f"\n使用template_id: {template_id}")
    
    # 测试获取模板内容
    print("\n" + "=" * 60)
    print(f"2. 获取模板内容")
    print("=" * 60)
    
    encoded_id = quote(template_id)
    content_response = requests.get(f"http://localhost:8000/api/templates/{encoded_id}/content")
    print(f"状态码: {content_response.status_code}")
    
    if content_response.status_code == 200:
        print(f"内容长度: {len(content_response.text)} 字符")
    else:
        print(f"错误: {content_response.text[:200]}")
else:
    print(f"错误: {response.text}")
