#!/usr/bin/env python3
"""检查所有教师相关表的字段"""
import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port='5432',
    database='taiping_education',
    user='taiping_user',
    password='taiping_password'
)
cursor = conn.cursor()

# 检查所有教师相关表
tables = ['teacher_basic_info', 'teacher_education_record', 'teachers']

for table in tables:
    print(f"\n{'='*60}")
    print(f"【{table} 表】")
    print('='*60)
    try:
        cursor.execute(f"""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = '{table}'
            ORDER BY ordinal_position
        """)
        for row in cursor.fetchall():
            print(f"  {row[0]}")
    except Exception as e:
        print(f"  错误: {e}")

cursor.close()
conn.close()
