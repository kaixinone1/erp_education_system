#!/usr/bin/env python3
"""修复模板文件 - 将硬编码的姓名替换为占位符"""
import re

template_path = r'd:\erp_thirteen\tp_education_system\backend\templates\职工退休申报表html.html'

# 读取模板
with open(template_path, 'r', encoding='utf-8') as f:
    content = f.read()

print(f"原始文件长度: {len(content)} 字符")

# 查找所有"王德"
wangde_count = content.count('王德')
print(f"\n找到 {wangde_count} 处'王德'")

# 替换所有"王德"为"{{姓名}}"
new_content = content.replace('王德', '{{姓名}}')

# 保存修改后的文件
with open(template_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print(f"\n已替换为'{{{{姓名}}}}'")
print(f"新文件长度: {len(new_content)} 字符")

# 验证
with open(template_path, 'r', encoding='utf-8') as f:
    verify_content = f.read()

wangde_remaining = verify_content.count('王德')
xingming_count = verify_content.count('{{姓名}}')

print(f"\n验证:")
print(f"  剩余'王德': {wangde_remaining} 处")
print(f"  '{{{{姓名}}}}': {xingming_count} 处")

if wangde_remaining == 0 and xingming_count > 0:
    print("\n✓ 修复成功！")
else:
    print("\n✗ 修复可能有问题")
