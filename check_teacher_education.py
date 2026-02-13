#!/usr/bin/env python3
"""检查 teacher_education_record 表中 education 字段"""
import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port='5432',
    database='taiping_education',
    user='taiping_user',
    password='taiping_password'
)
cursor = conn.cursor()

cursor.execute('SELECT id, id_card, education FROM teacher_education_record')
print("teacher_education_record 表 - education:")
for row in cursor.fetchall():
    print(f"  id={row[0]}, id_card={row[1]}: education={row[2]}")

cursor.close()
conn.close()
