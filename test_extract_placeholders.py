#!/usr/bin/env python3
"""测试提取模板中的占位符"""
import requests

# 获取模板内容
print("=" * 60)
print("获取模板内容并提取占位符")
print("=" * 60)

template_id = "职工退休申报表html"
response = requests.get(f"http://localhost:8000/api/templates/{template_id}/content")

if response.status_code == 200:
    content = response.text
    print(f"模板内容长度: {len(content)} 字符")
    
    # 提取占位符
    import re
    
    # 匹配 {{字段名}} 格式
    pattern = r'\{\{([^}]+)\}\}'
    matches = re.findall(pattern, content)
    
    # 去重并统计
    unique_placeholders = []
    seen = set()
    for match in matches:
        # 清理并验证
        cleaned = match.strip()
        if cleaned and len(cleaned) < 50 and re.search(r'[\u4e00-\u9fa5a-zA-Z]', cleaned):
            if cleaned not in seen:
                seen.add(cleaned)
                unique_placeholders.append(cleaned)
    
    print(f"\n找到 {len(unique_placeholders)} 个唯一占位符:\n")
    for i, ph in enumerate(sorted(unique_placeholders), 1):
        print(f"  {i:2d}. {{{{{ph}}}}}")
    
    # 按类型分类
    print("\n" + "=" * 60)
    print("按类型分类:")
    print("=" * 60)
    
    chinese_fields = [ph for ph in unique_placeholders if re.search(r'[\u4e00-\u9fa5]', ph)]
    english_fields = [ph for ph in unique_placeholders if re.search(r'[a-zA-Z]', ph) and not re.search(r'[\u4e00-\u9fa5]', ph)]
    mixed_fields = [ph for ph in unique_placeholders if ph not in chinese_fields and ph not in english_fields]
    
    print(f"\n纯中文字段 ({len(chinese_fields)} 个):")
    for ph in sorted(chinese_fields):
        print(f"  - {ph}")
    
    print(f"\n纯英文字段 ({len(english_fields)} 个):")
    for ph in sorted(english_fields):
        print(f"  - {ph}")
    
    if mixed_fields:
        print(f"\n混合字段 ({len(mixed_fields)} 个):")
        for ph in sorted(mixed_fields):
            print(f"  - {ph}")
    
else:
    print(f"获取模板失败: {response.status_code}")
    print(response.text)
