#!/usr/bin/env python3
"""
测试数据清理工具 - 清理测试表
"""

import sys
sys.path.append(r'd:\erp_thirteen\tp_education_system\backend')

from services.cleanup_service import CleanupService

print("=" * 80)
print("测试数据清理工具")
print("=" * 80)

service = CleanupService()

# 1. 先查看可清理的表列表
print("\n1. 查看可清理的表列表:")
tables = service.get_deletable_tables()
for table in tables:
    status = "✓" if table['exists_in_db'] else "✗"
    print(f"  {status} {table['chinese_name']} ({table['english_name']}) - {table['table_type']}")

# 2. 清理测试字典表
print("\n2. 清理测试字典表: dict_talent_type")
result = service.cleanup_table("dict_talent_type")
print(f"  成功: {result['success']}")
for msg in result['messages']:
    print(f"    ✓ {msg}")
for error in result['errors']:
    print(f"    ✗ {error}")

# 3. 清理测试子表
print("\n3. 清理测试子表: teacher_talent_type")
result = service.cleanup_table("teacher_talalent_type")
print(f"  成功: {result['success']}")
for msg in result['messages']:
    print(f"    ✓ {msg}")
for error in result['errors']:
    print(f"    ✗ {error}")

# 4. 再次查看可清理的表列表
print("\n4. 清理后查看可清理的表列表:")
tables = service.get_deletable_tables()
if tables:
    for table in tables:
        status = "✓" if table['exists_in_db'] else "✗"
        print(f"  {status} {table['chinese_name']} ({table['english_name']})")
else:
    print("  没有可清理的表")

print("\n" + "=" * 80)
print("测试完成!")
print("=" * 80)
