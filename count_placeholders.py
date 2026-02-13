#!/usr/bin/env python3
"""统计模板中每个占位符的出现次数"""
import requests
import re
from collections import Counter
from urllib.parse import quote

# 获取模板内容
template_id = "职工退休申报表html"
encoded_id = quote(template_id)
response = requests.get(f"http://localhost:8000/api/templates/{encoded_id}/content")

if response.status_code == 200:
    content = response.text
    
    # 提取所有占位符（不去重，统计次数）
    pattern = r'\{\{([^}]+)\}\}'
    matches = re.findall(pattern, content)
    
    # 清理并统计
    cleaned_matches = []
    for match in matches:
        cleaned = match.strip()
        if cleaned and len(cleaned) < 50 and re.search(r'[\u4e00-\u9fa5a-zA-Z]', cleaned):
            cleaned_matches.append(cleaned)
    
    # 统计每个占位符的出现次数
    counter = Counter(cleaned_matches)
    
    print("=" * 60)
    print("职工退休呈报表模板 - 占位符出现次数统计")
    print("=" * 60)
    print()
    
    # 按出现次数降序排列
    for field, count in counter.most_common():
        print(f"{field:15s} {count:3d}个")
    
    print()
    print("-" * 60)
    print(f"{'唯一字段数':15s} {len(counter):3d}个")
    print(f"{'占位符总数':15s} {sum(counter.values()):3d}个")
    print("=" * 60)
    
else:
    print(f"获取模板失败: {response.status_code}")
    print(response.text[:200])
