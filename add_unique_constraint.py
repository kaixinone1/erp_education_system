#!/usr/bin/env python3
"""为 retirement_report_data 表添加唯一约束"""
import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port='5432',
    database='taiping_education',
    user='taiping_user',
    password='taiping_password'
)
cursor = conn.cursor()

# 检查是否已存在唯一约束
cursor.execute("""
    SELECT constraint_name 
    FROM information_schema.table_constraints 
    WHERE table_name = 'retirement_report_data' 
    AND constraint_type = 'UNIQUE'
    AND constraint_name LIKE '%teacher_id%'
""")

existing = cursor.fetchone()
if existing:
    print(f"唯一约束已存在: {existing[0]}")
else:
    # 添加唯一约束
    cursor.execute("""
        ALTER TABLE retirement_report_data 
        ADD CONSTRAINT uk_retirement_report_teacher_id 
        UNIQUE (teacher_id)
    """)
    print("已添加唯一约束: uk_retirement_report_teacher_id")

conn.commit()
cursor.close()
conn.close()
