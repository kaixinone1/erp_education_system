#!/usr/bin/env python3
"""列出模板中的所有占位符"""
import re

template_path = r'd:\erp_thirteen\tp_education_system\backend\templates\职工退休申报表html.html'

with open(template_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 查找所有占位符
all_placeholders = re.findall(r'\{\{([^{}]+)\}\}', content)
all_placeholders = [p.strip() for p in all_placeholders]
unique_placeholders = sorted(list(set(all_placeholders)))

print(f"模板中的 {len(unique_placeholders)} 个唯一占位符:")
print("=" * 60)

for i, p in enumerate(unique_placeholders, 1):
    print(f"{i:2d}. {{{{ {p} }}}}")

print("=" * 60)

# 检查是否有基础字段
basic_fields = ['姓名', '性别', '身份证号码', '出生日期', '民族']
print("\n基础字段检查:")
for field in basic_fields:
    if field in unique_placeholders:
        print(f"  ✓ {field}")
    else:
        print(f"  ✗ {field} (缺失)")
