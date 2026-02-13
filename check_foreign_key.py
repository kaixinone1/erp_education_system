#!/usr/bin/env python3
"""检查 teacher_education_record 表的外键"""
import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port='5432',
    database='taiping_education',
    user='taiping_user',
    password='taiping_password'
)
cursor = conn.cursor()

# 检查外键
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
    WHERE tc.table_name = 'teacher_education_record'
    AND tc.constraint_type = 'FOREIGN KEY'
""")

print("teacher_education_record 表的外键：")
for row in cursor.fetchall():
    print(f"  {row[0]}: {row[1]} -> {row[2]}.{row[3]}")

# 检查 teacher_basic_info 表的主键
cursor.execute("""
    SELECT kcu.column_name
    FROM information_schema.table_constraints tc
    JOIN information_schema.key_column_usage kcu
        ON tc.constraint_name = kcu.constraint_name
    WHERE tc.table_name = 'teacher_basic_info'
    AND tc.constraint_type = 'PRIMARY KEY'
""")

print("\nteacher_basic_info 表的主键：")
for row in cursor.fetchall():
    print(f"  {row[0]}")

cursor.close()
conn.close()
