#!/usr/bin/env python3
"""
调试前端请求
"""
import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port='5432',
    database='taiping_education',
    user='taiping_user',
    password='taiping_password'
)
cursor = conn.cursor()

# 查看document_templates表中的数据
cursor.execute("SELECT id, template_id, template_name FROM document_templates ORDER BY created_at DESC")
rows = cursor.fetchall()

print("模板列表:")
for row in rows:
    print(f"  id={row[0]}, template_id='{row[1]}', name='{row[2]}'")

cursor.close()
conn.close()

print("\n请检查浏览器控制台，查看实际发送的URL")
print("正确的URL格式应该是: /api/template-field-mapping/template-placeholders/16")
