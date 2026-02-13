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

cursor.execute("SELECT id, template_name, file_path FROM document_templates LIMIT 1")
row = cursor.fetchone()

if row and row[2] and os.path.exists(row[2]):
    print(f"检查模板: {row[1]}")
    print(f"文件路径: {row[2]}")
    
    with open(row[2], 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找 {字段名} 格式的占位符
    pattern1 = r'\{([^{}]+)\}'
    matches1 = re.findall(pattern1, content)
    
    # 查找 {{字段名}} 格式的占位符
    pattern2 = r'\{\{([^{}]+)\}\}'
    matches2 = re.findall(pattern2, content)
    
    # 查找 input 标签的 name 属性
    pattern3 = r'<input[^>]*name=["\']([^"\']+)["\']'
    matches3 = re.findall(pattern3, content)
    
    print(f"\n找到的占位符 {{字段名}}: {len(matches1)} 个")
    for m in set(matches1):
        print(f"  - {m}")
    
    print(f"\n找到的占位符 {{{{字段名}}}}: {len(matches2)} 个")
    for m in set(matches2):
        print(f"  - {m}")
    
    print(f"\n找到的 input name: {len(matches3)} 个")
    for m in set(matches3):
        print(f"  - {m}")

cursor.close()
conn.close()
