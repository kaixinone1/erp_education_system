#!/usr/bin/env python3
"""
列出所有可用的模板
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

cursor.execute("""
    SELECT id, template_id, template_name, file_path
    FROM document_templates
    ORDER BY id
""")

print("=== 可用模板列表 ===\n")
for row in cursor.fetchall():
    print(f"ID: {row[0]}")
    print(f"Template ID: {row[1]}")
    print(f"Name: {row[2]}")
    print(f"Path: {row[3]}")
    print()

cursor.close()
conn.close()
