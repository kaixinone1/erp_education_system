#!/usr/bin/env python3
"""验证字段顺序"""
import requests

response = requests.get("http://localhost:8000/api/auto-table/retirement_report_data/schema")
data = response.json()

if data.get('status') == 'success':
    fields = data['data'].get('fields', [])
    
    # 找到关键字段的位置
    for i, field in enumerate(fields, 1):
        if field['name'] in ['文化程度', '是否独生子女', '个人身份', '入党年月']:
            print(f"{i}. {field['name']} -> {field.get('label', field['name'])}")
            
    # 验证顺序
    culture_idx = next((i for i, f in enumerate(fields) if f['name'] == '文化程度'), -1)
    only_child_idx = next((i for i, f in enumerate(fields) if f['name'] == '是否独生子女'), -1)
    identity_idx = next((i for i, f in enumerate(fields) if f['name'] == '个人身份'), -1)
    party_idx = next((i for i, f in enumerate(fields) if f['name'] == '入党年月'), -1)
    
    print(f"\n验证结果:")
    print(f"  文化程度: 第{culture_idx+1}位")
    print(f"  是否独生子女: 第{only_child_idx+1}位")
    print(f"  个人身份: 第{identity_idx+1}位")
    print(f"  入党年月: 第{party_idx+1}位")
    
    if only_child_idx < identity_idx < party_idx:
        print("\n✓ 顺序正确: 是否独生子女 -> 个人身份 -> 入党年月")
    else:
        print("\n✗ 顺序不正确")
