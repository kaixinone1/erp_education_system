#!/usr/bin/env python3
"""分析模板中所有占位符的实际格式"""
import re

# 读取模板
template_path = 'templates/职工退休申报表html.html'
with open(template_path, 'r', encoding='utf-8') as f:
    content = f.read()

print("=" * 80)
print("分析模板中所有占位符的实际格式")
print("=" * 80)

# 查找所有包含大括号的模式
all_braces = re.findall(r'.{0,30}\{[^{}]+\}.{0,30}', content)

print(f"\n找到 {len(all_braces)} 个包含大括号的片段：\n")

# 去重并分类
unique_formats = {}
for match in all_braces:
    # 提取占位符名称
    placeholder_match = re.search(r'\{([^{}]+)\}', match)
    if placeholder_match:
        placeholder = placeholder_match.group(1).strip()
        # 过滤CSS
        if any(c in placeholder for c in [';', '\n', '\t', 'mso-', 'font:', 'border:', 'color:', 'style:', 'background']):
            continue
        if '<' in placeholder or '>' in placeholder:
            continue
        if not re.search(r'[\u4e00-\u9fa5]', placeholder):
            continue
        if len(placeholder) > 50:
            continue
        
        # 记录格式
        if placeholder not in unique_formats:
            unique_formats[placeholder] = match

print(f"共 {len(unique_formats)} 个不同的占位符：\n")

# 按格式分类
formats = {
    '格式1: <span>{</span>{字段名}<span>}</span>': [],
    '格式2: <span>{</span>{字段名}': [],
    '格式3: {字段名}<span>}</span>': [],
    '格式4: {字段名}': [],
    '格式5: {{字段名}}': [],
    '其他': []
}

for placeholder, context in unique_formats.items():
    if '<' in context and '{</' in context and '>}</' in context:
        formats['格式1: <span>{</span>{字段名}<span>}</span>'].append(placeholder)
    elif '<' in context and '{</' in context:
        formats['格式2: <span>{</span>{字段名}'].append(placeholder)
    elif '<' in context and '>}</' in context:
        formats['格式3: {字段名}<span>}</span>'].append(placeholder)
    elif '{{' in context and '}}' in context:
        formats['格式5: {{字段名}}'].append(placeholder)
    elif '{' in context and '}' in context:
        formats['格式4: {字段名}'].append(placeholder)
    else:
        formats['其他'].append((placeholder, context))

for fmt, placeholders in formats.items():
    if placeholders:
        print(f"\n{fmt} ({len(placeholders)}个):")
        for ph in placeholders[:5]:
            print(f"  - {ph}")
        if len(placeholders) > 5:
            print(f"  ... 还有 {len(placeholders) - 5} 个")

print("\n" + "=" * 80)
