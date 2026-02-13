#!/usr/bin/env python3
"""
测试通用模板和字段映射系统
"""
import sys
sys.path.insert(0, r'd:\erp_thirteen\tp_education_system\backend')

from services.placeholder_extractor import extract_fields
from services.field_mapping_service import (
    get_table_fields_from_db,
    apply_system_field_names,
    auto_map_fields,
    get_intermediate_tables
)

print("=== 测试通用模板和字段映射系统 ===\n")

# 测试1: 获取中间表列表
print("测试1: 获取中间表列表")
tables = get_intermediate_tables()
print(f"找到 {len(tables)} 个中间表")
for table in tables[:5]:
    print(f"  - {table['name']}")

# 测试2: 获取表字段
print("\n测试2: 获取退休呈报数据表字段")
fields = get_table_fields_from_db('retirement_report_data')
fields = apply_system_field_names(fields)
print(f"找到 {len(fields)} 个字段")
for field in fields[:10]:
    print(f"  - {field['name']} ({field.get('label', 'N/A')})")

# 测试3: 从模板提取占位符
print("\n测试3: 从模板提取占位符")
template_path = r'd:\erp_thirteen\tp_education_system\backend\templates\职工退休申报表html.html'
import os
if os.path.exists(template_path):
    template_fields = extract_fields(template_path, '.html')
    print(f"找到 {len(template_fields)} 个占位符")
    
    # 去重
    seen = set()
    unique_placeholders = []
    for field in template_fields:
        name = field['name']
        if name not in seen:
            seen.add(name)
            unique_placeholders.append(name)
    
    print(f"去重后有 {len(unique_placeholders)} 个唯一占位符")
    print(f"前10个: {unique_placeholders[:10]}")
    
    # 测试4: 自动映射
    print("\n测试4: 自动映射占位符到表字段")
    mappings = auto_map_fields(unique_placeholders[:10], 'retirement_report_data')
    for mapping in mappings:
        status = "✓" if mapping['field'] else "✗"
        print(f"  {status} {mapping['placeholder']} -> {mapping.get('field_label', '未映射')}")
else:
    print(f"模板文件不存在: {template_path}")

print("\n=== 测试完成 ===")
