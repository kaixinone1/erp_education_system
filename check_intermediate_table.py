#!/usr/bin/env python3
"""检查中间表名"""
import psycopg2

conn = psycopg2.connect(
    host="localhost",
    port="5432",
    database="taiping_education",
    user="taiping_user",
    password="taiping_password"
)
cursor = conn.cursor()

print("=" * 60)
print("数据库中的中间表")
print("=" * 60)

cursor.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public' 
    AND table_name LIKE '%report%'
""")

for row in cursor.fetchall():
    print(f"  - {row[0]}")

cursor.close()
conn.close()
