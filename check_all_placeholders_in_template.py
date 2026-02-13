#!/usr/bin/env python3
"""检查模板中所有可能的占位符"""
import re

template_path = r'd:\erp_thirteen\tp_education_system\backend\templates\职工退休申报表html.html'

with open(template_path, 'r', encoding='utf-8') as f:
    content = f.read()

print("=" * 80)
print("模板中所有可能的占位符检查")
print("=" * 80)

# 1. 标准双大括号 {{字段名}}
print("\n【1】标准双大括号 {{字段名}}:")
pattern1 = r'\{\{([^{}]+)\}\}'
matches1 = re.findall(pattern1, content)
for m in sorted(set(matches1)):
    print(f"   {{{{ {m} }}}}")

# 2. 被HTML标签分割的情况
print("\n【2】被HTML标签分割的占位符:")
# 模式: <tag>{</tag>{字段名}<tag>}</tag>
pattern2 = r'<[^>]*>\{</[^>]*>\{([^{}]+)\}<[^>]*>\}</[^>]*>'
matches2 = re.findall(pattern2, content)
for m in sorted(set(matches2)):
    print(f"   {m}")

# 3. 单大括号 {字段名}
print("\n【3】单大括号 {字段名}:")
pattern3 = r'(?<![\{])\{([^{}]+)\}(?![\}])'
matches3 = re.findall(pattern3, content)
# 过滤CSS样式
filtered = []
for m in matches3:
    if any(c in m for c in [';', 'mso-', 'font:', 'border:', 'color:', 'style:', 'background']):
        continue
    if '<' in m or '>' in m:
        continue
    if len(m) > 50:
        continue
    filtered.append(m)

for m in sorted(set(filtered)):
    print(f"   {{{m}}}")

# 4. 检查是否有其他格式的占位符
print("\n【4】其他可能的占位符模式:")
# 查找所有包含中文的方括号、尖括号等
pattern4 = r'[\[\<\(\（]([\u4e00-\u9fa5]+)[\]\>\)\）]'
matches4 = re.findall(pattern4, content)
for m in sorted(set(matches4)):
    print(f"   {m}")

print("\n" + "=" * 80)
