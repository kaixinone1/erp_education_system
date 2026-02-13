#!/usr/bin/env python3
"""测试表结构API是否返回个人身份字段"""
import requests

response = requests.get('http://localhost:8000/api/table-schema/retirement_report_data')
data = response.json()

if data.get('status') == 'success':
    print("表结构字段：")
    for field in data['data']['fields']:
        print(f"  {field['name']}: {field['type']}")
    
    # 检查是否有个人身份字段
    field_names = [f['name'] for f in data['data']['fields']]
    if '个人身份' in field_names:
        print("\n✓ 个人身份字段已存在于表结构中")
    else:
        print("\n✗ 个人身份字段不存在于表结构中")
else:
    print("API 调用失败:", data)
