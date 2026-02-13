#!/usr/bin/env python3
"""检查 business_checklist 表字段"""
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
    WHERE table_name = 'business_checklist'
    ORDER BY ordinal_position
""")

print("business_checklist 表字段：")
for row in cursor.fetchall():
    print(f"  {row[0]}")

cursor.close()
conn.close()
