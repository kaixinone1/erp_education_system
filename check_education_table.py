#!/usr/bin/env python3
"""
检查学历表结构
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

# 检查 teacher_education_record 表结构
cursor.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = 'teacher_education_record'
    ORDER BY ordinal_position
""")

print("=== teacher_education_record 表结构 ===\n")
for row in cursor.fetchall():
    print(f"  {row[0]}: {row[1]}")

cursor.close()
conn.close()
