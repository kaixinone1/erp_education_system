#!/usr/bin/env python3
"""检查是否独生子女字段"""
import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port='5432',
    database='taiping_education',
    user='taiping_user',
    password='taiping_password'
)
cursor = conn.cursor()

# 检查 retirement_report_data 表
cursor.execute('SELECT teacher_id, "是否独生子女" FROM retirement_report_data LIMIT 5')
print("retirement_report_data 表 - 是否独生子女:")
for row in cursor.fetchall():
    print(f"  teacher_id={row[0]}, 是否独生子女={row[1]}")

# 检查 teacher_basic_info 表是否有这个字段
cursor.execute("""
    SELECT column_name 
    FROM information_schema.columns 
    WHERE table_name = 'teacher_basic_info' AND column_name LIKE '%独生%'
""")
print("\nteacher_basic_info 表是否有 是否独生子女 字段:")
rows = cursor.fetchall()
if rows:
    for row in rows:
        print(f"  {row[0]}")
else:
    print("  没有这个字段")

cursor.close()
conn.close()
