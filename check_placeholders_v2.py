#!/usr/bin/env python3
import psycopg2
import os
import re

conn = psycopg2.connect(
    host='localhost',
    port='5432',
    database='taiping_education',
    user='taiping_user',
    password='taiping_password'
)
cursor = conn.cursor()

cursor.execute("SELECT id, template_name, file_path FROM document_templates ORDER BY created_at DESC LIMIT 1")
row = cursor.fetchone()

if row and row[2] and os.path.exists(row[2]):
    print(f"检查模板: {row[1]}")
    
    with open(row[2], 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 使用新的过滤逻辑
    def is_valid_placeholder(match):
        match = match.strip()
        if not match:
            return False
        if any(keyword in match for keyword in ['mso-', 'style0', 'font-', 'border-', 'padding', 'margin', 'color:', 'background', 'text-align', 'white-space']):
            return False
        if match.isdigit():
            return False
        if ':' in match or ';' in match or '{' in match or '}' in match:
            return False
        if len(match) > 50:
            return False
        if not re.match(r'^[\u4e00-\u9fa5a-zA-Z0-9_\s]+$', match):
            return False
        return True
    
    # 方法1: HTML标签中
    pattern1 = r'>([^<]*\{[^{}]+\}[^<]*)<'
    matches1 = re.findall(pattern1, content)
    
    all_placeholders = []
    for m in matches1:
        inner_matches = re.findall(r'\{([^{}]+)\}', m)
        for inner in inner_matches:
            if is_valid_placeholder(inner):
                all_placeholders.append(inner.strip())
    
    # 方法2: input标签
    pattern2 = r'<input[^>]*(?:value|placeholder)=["\']?\{([^{}]+)\}["\']?[^>]*>'
    matches2 = re.findall(pattern2, content, re.IGNORECASE)
    for m in matches2:
        if is_valid_placeholder(m):
            all_placeholders.append(m.strip())
    
    # 去重
    seen = set()
    unique = []
    for p in all_placeholders:
        if p not in seen:
            seen.add(p)
            unique.append(p)
    
    print(f"\n找到的有效占位符: {len(unique)} 个")
    for p in unique:
        print(f"  - {{{p}}}")

cursor.close()
conn.close()
