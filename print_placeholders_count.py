#!/usr/bin/env python3
"""按格式打印占位符及其出现次数"""
import re
from collections import Counter

template_path = r'd:\erp_thirteen\tp_education_system\backend\templates\职工退休申报表html.html'

with open(template_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 提取所有双大括号占位符
pattern = r'\{\{([^{}]+)\}\}'
matches = re.findall(pattern, content)

# 统计每个占位符出现的次数
counter = Counter(matches)

print("=" * 50)
print("占位符统计")
print("=" * 50)

# 按出现次数降序排列
for placeholder, count in counter.most_common():
    print(f"{placeholder}：{count}")

print("=" * 50)
print(f"总计：{len(counter)} 个唯一占位符，{sum(counter.values())} 次出现")
