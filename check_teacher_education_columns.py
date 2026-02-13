#!/usr/bin/env python3
"""检查教师学历记录表的列名"""
import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port=5432,
    database='taiping_education',
    user='taiping_user',
    password='taiping_password'
)
cursor = conn.cursor()

cursor.execute("""
    SELECT column_name, data_type
    FROM information_schema.columns
    WHERE table_name = 'teacher_education_record'
    ORDER BY ordinal_position
""")

print("教师学历记录表的列:")
for row in cursor.fetchall():
    print(f"  - {row[0]}: {row[1]}")

cursor.close()
conn.close()
