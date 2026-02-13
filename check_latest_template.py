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

# 获取最新的模板
cursor.execute("""
    SELECT id, template_id, template_name, file_path, file_name, created_at
    FROM document_templates
    ORDER BY created_at DESC
    LIMIT 1
""")

row = cursor.fetchone()

if row:
    print(f"最新模板信息：")
    print(f"  id: {row[0]}")
    print(f"  template_id: {row[1]}")
    print(f"  template_name: {row[2]}")
    print(f"  file_path: {row[3]}")
    print(f"  file_name: {row[4]}")
    print(f"  created_at: {row[5]}")
    
    file_path = row[3]
    print(f"\n文件是否存在: {os.path.exists(file_path) if file_path else False}")
    
    if file_path and os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找 {字段名} 格式的占位符
        pattern = r'\{([^{}]+)\}'
        matches = re.findall(pattern, content)
        
        print(f"\n找到的占位符: {len(set(matches))} 个")
        for m in sorted(set(matches)):
            print(f"  - {{{m}}}")
        
        # 显示文件内容片段（包含占位符的部分）
        if matches:
            print("\n包含占位符的内容片段：")
            for match in set(matches):
                idx = content.find('{' + match + '}')
                if idx >= 0:
                    start = max(0, idx - 50)
                    end = min(len(content), idx + len(match) + 52)
                    snippet = content[start:end]
                    print(f"\n...{snippet}...")
                    break

cursor.close()
conn.close()
