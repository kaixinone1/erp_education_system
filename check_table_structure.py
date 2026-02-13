#!/usr/bin/env python3
"""检查 retirement_report_data 表结构"""
import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port='5432',
    database='taiping_education',
    user='taiping_user',
    password='taiping_password'
)
cursor = conn.cursor()

# 检查 retirement_report_data 表的列
cursor.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = 'retirement_report_data'
    ORDER BY ordinal_position
""")

print("retirement_report_data 表结构：")
for row in cursor.fetchall():
    print(f"  {row[0]}: {row[1]}")

cursor.close()
conn.close()
