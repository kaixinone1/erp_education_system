#!/usr/bin/env python3
"""
检查父表ID映射
"""

import sys
sys.path.append(r'd:\erp_thirteen\tp_education_system\backend')

from services.import_service import ImportService

service = ImportService()

# 获取父表ID映射
parent_id_map = service._get_parent_id_map('teacher_basic')
parent_name_map = service._get_parent_name_map('teacher_basic')

print(f"父表 teacher_basic 的ID映射数量: {len(parent_id_map)}")
print(f"父表 teacher_basic 的姓名映射数量: {len(parent_name_map)}")

print("\n前10个映射示例:")
for i, (k, v) in enumerate(list(parent_id_map.items())[:10]):
    name = parent_name_map.get(k, '未知')
    print(f"  身份证: {k} -> ID: {v}, 姓名: {name}")
