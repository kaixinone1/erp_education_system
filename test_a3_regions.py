#!/usr/bin/env python3
"""测试A3区域检测"""
import requests

# 测试第1页
template_id = "test_template_1770691934"
print("=" * 60)
print("测试第1页区域检测")
print("=" * 60)

url1 = f"http://localhost:8000/api/templates/{template_id}/a3-regions?page=1"
response1 = requests.get(url1)
print(f"状态码: {response1.status_code}")
if response1.status_code == 200:
    result1 = response1.json()
    print(f"是否A3: {result1.get('is_a3')}")
    print(f"页面: {result1.get('page')}")
    print(f"页面尺寸: {result1.get('page_width')} x {result1.get('page_height')} pt")
    regions1 = result1.get('regions', [])
    print(f"区域数量: {len(regions1)}")
    for r in regions1:
        print(f"\n  区域{r['id']}: {r['name']}")
        print(f"    页码: {r['page']}")
        bounds = r['bounds']
        print(f"    边界: x0={bounds['x0']:.1f}, y0={bounds['y0']:.1f}, x1={bounds['x1']:.1f}, y1={bounds['y1']:.1f}")
        width = bounds['x1'] - bounds['x0']
        print(f"    宽度: {width:.1f} pt ({width*0.3528:.1f} mm)")

print("\n" + "=" * 60)
print("测试第2页区域检测")
print("=" * 60)

url2 = f"http://localhost:8000/api/templates/{template_id}/a3-regions?page=2"
response2 = requests.get(url2)
print(f"状态码: {response2.status_code}")
if response2.status_code == 200:
    result2 = response2.json()
    print(f"是否A3: {result2.get('is_a3')}")
    print(f"页面: {result2.get('page')}")
    regions2 = result2.get('regions', [])
    print(f"区域数量: {len(regions2)}")
    for r in regions2:
        print(f"\n  区域{r['id']}: {r['name']}")
        print(f"    页码: {r['page']}")
        bounds = r['bounds']
        print(f"    边界: x0={bounds['x0']:.1f}, y0={bounds['y0']:.1f}, x1={bounds['x1']:.1f}, y1={bounds['y1']:.1f}")
