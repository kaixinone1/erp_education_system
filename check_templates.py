#!/usr/bin/env python3
"""
检查模板ID
"""
import sys
sys.path.insert(0, r'd:\erp_thirteen\tp_education_system\backend')

import psycopg2

def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        port="5432",
        database="taiping_education",
        user="taiping_user",
        password="taiping_password"
    )

conn = get_db_connection()
cursor = conn.cursor()

# 使用 id 查询
cursor.execute("SELECT id, template_id, template_name FROM document_templates WHERE id = 21")
row = cursor.fetchone()
print("=== 使用 id=21 查询 ===")
print(f"结果: {row}")

# 列出所有模板
cursor.execute("SELECT id, template_id, template_name FROM document_templates")
rows = cursor.fetchall()
print("\n=== 所有模板 ===")
for row in rows:
    print(f"ID: {row[0]}, Template ID: {row[1]}, Name: {row[2]}")

cursor.close()
conn.close()
