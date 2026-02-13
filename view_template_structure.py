#!/usr/bin/env python3
import psycopg2
import os

conn = psycopg2.connect(
    host='localhost',
    port='5432',
    database='taiping_education',
    user='taiping_user',
    password='taiping_password'
)
cursor = conn.cursor()

cursor.execute("SELECT file_path FROM document_templates ORDER BY created_at DESC LIMIT 1")
row = cursor.fetchone()

if row and row[0] and os.path.exists(row[0]):
    with open(row[0], 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找表格单元格内容
    import re
    # 查找所有 <td>...</td> 中的内容
    tds = re.findall(r'<td[^>]*>(.*?)</td>', content, re.DOTALL)
    
    print("模板中的表格单元格内容（前30个）：")
    for i, td in enumerate(tds[:30]):
        # 清理HTML标签
        text = re.sub(r'<[^>]+>', '', td).strip()
        if text:
            print(f"  {i+1}. {text[:50]}")

cursor.close()
conn.close()
