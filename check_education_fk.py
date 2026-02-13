#!/usr/bin/env python3
"""
检查学历表的外键关系
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

# 查询学历表的一条数据看看字段
cursor.execute("SELECT * FROM teacher_education_record LIMIT 1")

if cursor.description:
    columns = [desc[0] for desc in cursor.description]
    print("=== teacher_education_record 表字段 ===\n")
    for i, col in enumerate(columns):
        print(f"  {i}: {col}")
    
    row = cursor.fetchone()
    if row:
        print("\n=== 示例数据 ===\n")
        for i, col in enumerate(columns):
            print(f"  {col}: {row[i]}")

# 检查是否有外键约束
cursor.execute("""
    SELECT
        tc.constraint_name,
        kcu.column_name,
        ccu.table_name AS foreign_table_name,
        ccu.column_name AS foreign_column_name
    FROM
        information_schema.table_constraints AS tc
        JOIN information_schema.key_column_usage AS kcu
            ON tc.constraint_name = kcu.constraint_name
        JOIN information_schema.constraint_column_usage AS ccu
            ON ccu.constraint_name = tc.constraint_name
    WHERE tc.constraint_type = 'FOREIGN KEY'
        AND tc.table_name = 'teacher_education_record'
""")

print("\n=== 外键关系 ===\n")
fk_rows = cursor.fetchall()
if fk_rows:
    for row in fk_rows:
        print(f"  {row[0]}: {row[1]} -> {row[2]}.{row[3]}")
else:
    print("  无外键约束")

cursor.close()
conn.close()
