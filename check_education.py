#!/usr/bin/env python3
"""检查文化程度字段"""
import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port='5432',
    database='taiping_education',
    user='taiping_user',
    password='taiping_password'
)
cursor = conn.cursor()

cursor.execute('SELECT teacher_id, "文化程度" FROM retirement_report_data')
print("retirement_report_data 表 - 文化程度:")
for row in cursor.fetchall():
    print(f"  teacher_id={row[0]}: {row[1]}")

cursor.close()
conn.close()
