#!/usr/bin/env python3
"""检查 teacher_basic_info 表字段"""
import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port='5432',
    database='taiping_education',
    user='taiping_user',
    password='taiping_password'
)
cursor = conn.cursor()

cursor.execute("""
    SELECT column_name 
    FROM information_schema.columns 
    WHERE table_name = 'teacher_basic_info'
    ORDER BY ordinal_position
""")

print("teacher_basic_info 表字段：")
for row in cursor.fetchall():
    print(f"  {row[0]}")

# 检查教师ID 273的数据
cursor.execute("SELECT * FROM teacher_basic_info WHERE id = 273")
row = cursor.fetchone()
if row:
    print("\n教师ID 273的数据：")
    cursor.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'teacher_basic_info'
        ORDER BY ordinal_position
    """)
    columns = cursor.fetchall()
    for i, col in enumerate(columns):
        if i < len(row):
            print(f"  {col[0]}: {row[i]}")

cursor.close()
conn.close()
