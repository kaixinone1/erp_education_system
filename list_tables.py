#!/usr/bin/env python3
"""列出所有表"""
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
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public'
    ORDER BY table_name
""")

print("数据库中的所有表：")
for row in cursor.fetchall():
    print(f"  {row[0]}")

cursor.close()
conn.close()
