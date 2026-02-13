#!/usr/bin/env python3
"""
检查映射数据
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

# 检查 template_field_mapping 中的数据
cursor.execute("""
    SELECT id, template_id, template_name, placeholder_name, intermediate_field
    FROM template_field_mapping
    LIMIT 10
""")

print("=== template_field_mapping 数据 ===\n")
for row in cursor.fetchall():
    print(f"ID: {row[0]}, Template ID: {row[1]}, Template: {row[2][:30] if row[2] else ''}")
    print(f"  Placeholder: {row[3]}, Field: {row[4]}")
    print()

cursor.close()
conn.close()
