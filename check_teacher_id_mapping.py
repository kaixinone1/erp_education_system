#!/usr/bin/env python3
"""检查 teacher_basic_info 表的 id 和 id_card 对应关系"""
import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port='5432',
    database='taiping_education',
    user='taiping_user',
    password='taiping_password'
)
cursor = conn.cursor()

cursor.execute('SELECT id, id_card FROM teacher_basic_info WHERE id IN (273, 299)')
print("teacher_basic_info 表 - id 和 id_card 对应关系:")
for row in cursor.fetchall():
    print(f"  id={row[0]}, id_card={row[1]}")

cursor.close()
conn.close()
