#!/usr/bin/env python3
"""
测试通用占位符提取功能
"""
import sys
sys.path.insert(0, r'd:\erp_thirteen\tp_education_system\backend')

from services.placeholder_extractor import (
    extract_placeholders_from_text,
    extract_from_html,
    load_config
)

# 测试1: 从文本中提取占位符
print("=== 测试1: 从文本中提取占位符 ===")
test_text = """
<html>
<body>
<p>姓名: {姓名}</p>
<p>性别: {性别}</p>
<p>年龄: {年龄}</p>
<style>
.xl91 {{mso-style-parent:style0;}}
</style>
</body>
</html>
"""

config = load_config()
placeholders = extract_placeholders_from_text(test_text, config)
print(f"找到的占位符: {placeholders}")
print(f"数量: {len(placeholders)}")

# 测试2: 从HTML文件中提取
print("\n=== 测试2: 从HTML文件中提取 ===")
template_path = r'd:\erp_thirteen\tp_education_system\backend\templates\职工退休申报表html.html'
import os
if os.path.exists(template_path):
    fields = extract_from_html(template_path)
    print(f"找到的字段数: {len(fields)}")
    print("前10个字段:")
    for field in fields[:10]:
        print(f"  - {field['name']} (来源: {field.get('source', 'unknown')})")
else:
    print(f"模板文件不存在: {template_path}")

print("\n=== 测试完成 ===")
