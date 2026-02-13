#!/usr/bin/env python3
import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port='5432',
    database='taiping_education',
    user='taiping_user',
    password='taiping_password'
)
cursor = conn.cursor()

# 查询模板
cursor.execute("SELECT id, template_id, file_path FROM document_templates WHERE template_id = %s", ('职工退休申报表html',))
row = cursor.fetchone()

if row:
    print(f"找到模板:")
    print(f"  id: {row[0]}")
    print(f"  template_id: {row[1]}")
    print(f"  file_path: {row[2]}")
else:
    print("未找到模板")
    
    # 查询所有模板
    print("\n所有模板:")
    cursor.execute("SELECT id, template_id FROM document_templates")
    for r in cursor.fetchall():
        print(f"  id={r[0]}, template_id={r[1]}")

cursor.close()
conn.close()
