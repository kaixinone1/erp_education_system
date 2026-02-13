#!/usr/bin/env python3
"""测试四角数据格式"""
import requests

template_id = "test_template_1770691934"
url = f"http://localhost:8000/api/templates/{template_id}/a3-regions?page=1"

response = requests.get(url)
result = response.json()

if result.get('status') == 'success' and result.get('is_a3'):
    print("区域数据:")
    for region in result['regions']:
        print(f"\n区域 {region['id']}: {region['name']}")
        print(f"  corners类型: {type(region['corners'])}")
        print(f"  corners数量: {len(region['corners'])}")
        for i, corner in enumerate(region['corners']):
            print(f"    角{i}: {corner}")
