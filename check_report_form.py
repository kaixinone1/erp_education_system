#!/usr/bin/env python3
"""检查 retirement_report_form 表中的数据"""
import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port='5432',
    database='taiping_education',
    user='taiping_user',
    password='taiping_password'
)
cursor = conn.cursor()

# 检查 retirement_report_form 表中是否独生子女的实际值
cursor.execute('SELECT teacher_id, is_only_child FROM retirement_report_form ORDER BY teacher_id')
print("retirement_report_form 表 - is_only_child:")
for row in cursor.fetchall():
    teacher_id = row[0]
    val = row[1]
    if val is None:
        display = "NULL"
    elif val == True:
        display = "True (是)"
    elif val == False:
        display = "False (否)"
    else:
        display = str(val)
    print(f"  teacher_id={teacher_id}: {display}")

cursor.close()
conn.close()
