#!/usr/bin/env python3
"""
测试简单占位符提取器
"""
import sys
sys.path.insert(0, r'd:\erp_thirteen\tp_education_system\backend')

from services.simple_placeholder_extractor import extract_fields, extract_from_text

print("=== 测试简单占位符提取器 ===\n")

# 测试1: 从文本提取
print("测试1: 从文本提取")
test_content = """
<html>
<body>
<p>姓名: {姓名}</p>
<p>性别: {性别}</p>
<p>出生日期: {出生日期}</p>
<p>岗位: [岗位]</p>
<style>
.xl91 {{mso-style-parent:style0;}}
</style>
</body>
</html>
"""

placeholders = extract_from_text(test_content)
print(f"找到的占位符: {placeholders}")
print(f"数量: {len(placeholders)}")

# 测试2: 从HTML文件提取
print("\n测试2: 从HTML文件提取")
template_path = r'd:\erp_thirteen\tp_education_system\backend\templates\职工退休申报表html.html'
import os
if os.path.exists(template_path):
    fields = extract_fields(template_path, '.html')
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
    print(f"前15个: {unique[:15]}")
else:
    print(f"模板文件不存在: {template_path}")

# 测试3: 测试其他模板（如果有）
print("\n测试3: 查找其他模板文件")
templates_dir = r'd:\erp_thirteen\tp_education_system\backend\templates'
if os.path.exists(templates_dir):
    files = os.listdir(templates_dir)
    html_files = [f for f in files if f.endswith('.html') or f.endswith('.htm')]
    print(f"找到 {len(html_files)} 个HTML模板文件:")
    for f in html_files[:5]:
        print(f"  - {f}")

print("\n=== 测试完成 ===")
