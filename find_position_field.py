#!/usr/bin/env python3
import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port=5432,
    database='taiping_education',
    user='taiping_user',
    password='taiping_password'
)
cursor = conn.cursor()

# 查找包含"岗位"的字段
cursor.execute("""
    SELECT table_name, column_name 
    FROM information_schema.columns 
    WHERE table_schema = 'public' 
    AND (column_name LIKE '%岗位%' OR column_name LIKE '%position%')
    ORDER BY table_name, column_name
""")
fields = cursor.fetchall()
print("包含'岗位'的字段:")
for table, column in fields:
    print(f"  - {table}.{column}")

# 查看 teacher_basic_info 表的所有字段
cursor.execute("""
    SELECT column_name 
    FROM information_schema.columns 
    WHERE table_name = 'teacher_basic_info'
    ORDER BY ordinal_position
""")
columns = cursor.fetchall()
print(f"\nteacher_basic_info 表的所有字段:")
for col in columns:
    print(f"  - {col[0]}")

# 查看 teacher_title_info 表的数据样例
cursor.execute("SELECT DISTINCT professional_title_1 FROM teacher_title_info WHERE professional_title_1 IS NOT NULL LIMIT 20")
titles = cursor.fetchall()
print(f"\nprofessional_title_1 示例值:")
for t in titles:
    print(f"  - {t[0]}")

cursor.close()
conn.close()
