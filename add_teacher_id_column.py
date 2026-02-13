#!/usr/bin/env python3
"""为 teacher_education_record 表添加 teacher_id 字段"""
import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port='5432',
    database='taiping_education',
    user='taiping_user',
    password='taiping_password'
)
cursor = conn.cursor()

# 检查 teacher_id 字段是否已存在
cursor.execute("""
    SELECT column_name 
    FROM information_schema.columns 
    WHERE table_name = 'teacher_education_record' AND column_name = 'teacher_id'
""")

if cursor.fetchone():
    print("teacher_id 字段已存在")
else:
    # 添加 teacher_id 字段
    cursor.execute("""
        ALTER TABLE teacher_education_record 
        ADD COLUMN teacher_id INTEGER
    """)
    print("已添加 teacher_id 字段")

conn.commit()
cursor.close()
conn.close()
