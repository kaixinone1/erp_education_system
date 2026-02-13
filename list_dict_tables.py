#!/usr/bin/env python3
"""列出所有字典表"""
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
    AND table_name LIKE 'dict_%'
    ORDER BY table_name
""")

print("字典表列表：")
for row in cursor.fetchall():
    print(f"  {row[0]}")

cursor.close()
conn.close()
