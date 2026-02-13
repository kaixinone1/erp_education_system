#!/usr/bin/env python3
"""
测试通用占位符提取器
"""
import sys
sys.path.insert(0, r'd:\erp_thirteen\tp_education_system\backend')

from services.universal_placeholder_extractor import extract_fields

template_path = r'd:\erp_thirteen\tp_education_system\backend\templates\枣阳市机关事业单位养老保险改革过渡期内职务升降退休人员信息申报表htm.htm'

print("=== 测试通用占位符提取器 ===\n")

import os
if os.path.exists(template_path):
    fields = extract_fields(template_path, '.htm')
    print(f"找到的字段数: {len(fields)}")
    
    # 去重
    seen = set()
    unique = []
    for f in fields:
        name = f['name']
        if name not in seen:
            seen.add(name)
            unique.append(name)
    
    print(f"去重后有 {len(unique)} 个唯一占位符")
    print(f"\n所有占位符:")
    for i, name in enumerate(unique, 1):
        print(f"  {i}. {name}")
else:
    print(f"模板文件不存在: {template_path}")

print("\n=== 测试完成 ===")
