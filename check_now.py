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

print('数据库中的教师数据：')
for tid in [273, 299]:
    cursor.execute('SELECT teacher_id, "姓名" FROM retirement_report_data WHERE teacher_id = %s', (tid,))
    row = cursor.fetchone()
    print(f'  教师ID {row[0]}: {row[1]}')

cursor.close()
conn.close()
