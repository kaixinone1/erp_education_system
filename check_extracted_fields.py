#!/usr/bin/env python3
"""检查提取的字段详情"""
import requests

template_id = "test_template_1770691934"
url = f"http://localhost:8000/api/templates/{template_id}/a3-regions/extract"

data = {
    "page": 1,
    "regions": [
        {
            "id": 1,
            "bounds": {"x0": 85, "y0": 85, "x1": 585.3, "y1": 756.9}
        },
        {
            "id": 2,
            "bounds": {"x0": 605.3, "y0": 85, "x1": 1105.5, "y1": 756.9}
        }
    ]
}

response = requests.post(url, json=data)
result = response.json()

print(f"提取到 {result['fields_count']} 个字段:\n")

for i, f in enumerate(result['fields'], 1):
    print(f"{i}. 名称: {f['name']}")
    print(f"   标签: {f['label']}")
    print(f"   位置: ({f['x']:.1f}, {f['y']:.1f})")
    print(f"   尺寸: {f['width']:.1f} x {f['height']:.1f}")
    print(f"   区域: {f['region_id']}")
    print(f"   类型: {f['type']}")
    print()
