#!/usr/bin/env python3
"""测试V2版本提取器"""
import sys
sys.path.insert(0, 'd:\\erp_thirteen\\tp_education_system\\backend')

from services.field_extractor_v2 import extract_pdf_fields
import json

pdf_path = "d:\\erp_thirteen\\tp_education_system\\backend\\templates\\职工退休申报表.pdf"

print("测试V2版本字段提取...\n")
fields = extract_pdf_fields(pdf_path)

print(f"共提取到 {len(fields)} 个字段:\n")
print(f"{'字段名':<20} {'标签':<20} {'页码':<6} {'X坐标':<10} {'Y坐标':<10}")
print("-" * 70)

for field in fields[:20]:  # 只显示前20个
    print(f"{field['name']:<20} {field['label']:<20} {field['page']:<6} "
          f"{field['x']:<10.1f} {field['y']:<10.1f}")

# 查找"姓名"字段
print("\n" + "="*70)
print("查找'姓名'字段:")
for field in fields:
    if '姓名' in field['name']:
        print(f"  找到: {field}")
