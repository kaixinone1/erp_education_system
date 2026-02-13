#!/usr/bin/env python3
"""
测试中文表名返回
"""
import sys
sys.path.insert(0, r'd:\erp_thirteen\tp_education_system\backend')

from services.field_mapping_service import get_intermediate_tables

print("=== 测试中文表名 ===\n")

tables = get_intermediate_tables()
print(f"找到 {len(tables)} 个中间表:\n")

for table in tables:
    print(f"  英文名: {table['name']}")
    print(f"  中文名: {table['label']}")
    print()

print("=== 测试完成 ===")
