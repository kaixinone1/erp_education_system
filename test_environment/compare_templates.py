#!/usr/bin/env python3
"""比较原始模板和当前模板"""
import re

# 当前模板
current_path = r'd:\erp_thirteen\tp_education_system\backend\templates\职工退休申报表html.html'
# 备份模板
backup_path = r'd:\erp_thirteen\tp_education_system\backend\templates\职工退休申报表_v20260212_130634.html'

with open(current_path, 'r', encoding='utf-8') as f:
    current = f.read()

with open(backup_path, 'r', encoding='utf-8') as f:
    backup = f.read()

print("=" * 70)
print("模板文件比较")
print("=" * 70)

print("\n【当前模板】")
print(f"   文件大小: {len(current)} 字符")
if '王德' in current:
    print(f"   ✗ 包含硬编码'王德': {current.count('王德')} 次")
else:
    print(f"   ✓ 无硬编码'王德'")

name_placeholders_current = len(re.findall(r'\{\{\s*姓名\s*\}\}', current))
print(f"   {{姓名}}占位符: {name_placeholders_current} 个")

print("\n【备份模板】")
print(f"   文件大小: {len(backup)} 字符")
if '王德' in backup:
    print(f"   ✗ 包含硬编码'王德': {backup.count('王德')} 次")
else:
    print(f"   ✓ 无硬编码'王德'")

name_placeholders_backup = len(re.findall(r'\{\{\s*姓名\s*\}\}', backup))
print(f"   {{姓名}}占位符: {name_placeholders_backup} 个")

print("\n【差异分析】")
if len(current) != len(backup):
    print(f"   文件大小不同: 当前{len(current)} vs 备份{len(backup)}")
    
    # 找出差异
    if '王德' in backup and '王德' not in current:
        print(f"   当前模板已移除'王德'")
    
    if name_placeholders_current > name_placeholders_backup:
        print(f"   当前模板添加了{{{{姓名}}}}占位符")

print("\n" + "=" * 70)
