#!/usr/bin/env python3
import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port='5432',
    database='taiping_education',
    user='taiping_user',
    password='taiping_password'
)
cursor = conn.cursor()

# 查询所有表名
cursor.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public'
    ORDER BY table_name
""")

rows = cursor.fetchall()
print("数据库中的所有表：")
for row in rows:
    print(f"  - {row[0]}")

# 查找包含 module 的表
print("\n包含 'module' 的表：")
cursor.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public' 
    AND table_name LIKE '%module%'
    ORDER BY table_name
""")

rows = cursor.fetchall()
if rows:
    for row in rows:
        print(f"  - {row[0]}")
else:
    print("  没有找到包含 'module' 的表")

cursor.close()
conn.close()
