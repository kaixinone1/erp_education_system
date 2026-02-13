#!/usr/bin/env python3
"""
测试获取表字段API
"""
import requests

# 测试API
url = "http://localhost:8000/api/template-field-mapping/table-fields/retirement_report_data"

print("=== 测试获取表字段API ===\n")

try:
    response = requests.get(url)
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"状态: {result.get('status')}")
        print(f"表名: {result.get('table_name')}")
        print(f"表中文名: {result.get('table_name_cn')}")
        fields = result.get('fields', [])
        print(f"字段数: {len(fields)}")
        print("\n前10个字段:")
        for field in fields[:10]:
            print(f"  - {field.get('name')} ({field.get('name_cn')})")
    else:
        print(f"请求失败: {response.text}")
except Exception as e:
    print(f"错误: {e}")

print("\n=== 测试完成 ===")
