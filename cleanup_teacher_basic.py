#!/usr/bin/env python3
"""
清理 teacher_basic 测试表
"""

import sys
sys.path.append(r'd:\erp_thirteen\tp_education_system\backend')

from services.cleanup_service import CleanupService

print("=" * 80)
print("清理 teacher_basic 测试表")
print("=" * 80)

service = CleanupService()

# 清理 teacher_basic 表
print("\n清理表: teacher_basic")
result = service.cleanup_table("teacher_basic")

print(f"  成功: {result['success']}")

if result['messages']:
    print("\n  清理内容:")
    for msg in result['messages']:
        print(f"    ✓ {msg}")

if result['errors']:
    print("\n  错误:")
    for error in result['errors']:
        print(f"    ✗ {error}")

print("\n" + "=" * 80)
print("清理完成!")
print("=" * 80)
