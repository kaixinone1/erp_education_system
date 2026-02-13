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

cursor.execute("SELECT id, template_id, template_name, file_path, file_name FROM document_templates LIMIT 1")
row = cursor.fetchone()

if row:
    print(f"模板信息：")
    print(f"  id: {row[0]}")
    print(f"  template_id: {row[1]}")
    print(f"  template_name: {row[2]}")
    print(f"  file_path: {row[3]}")
    print(f"  file_name: {row[4]}")
    
    file_path = row[3]
    print(f"\n文件路径: {file_path}")
    print(f"文件是否存在: {os.path.exists(file_path) if file_path else False}")
    
    if file_path and os.path.exists(file_path):
        print(f"\n文件内容前500字符：")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read(500)
                print(content)
        except Exception as e:
            print(f"读取失败: {e}")

cursor.close()
conn.close()
