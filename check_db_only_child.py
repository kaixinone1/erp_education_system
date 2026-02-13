#!/usr/bin/env python3
"""检查数据库中是否独生子女字段"""
import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port='5432',
    database='taiping_education',
    user='taiping_user',
    password='taiping_password'
)
cursor = conn.cursor()

# 检查 retirement_report_data 表
cursor.execute('SELECT teacher_id, "是否独生子女" FROM retirement_report_data')
print("retirement_report_data 表 - 是否独生子女:")
for row in cursor.fetchall():
    val = row[1]
    if val is None:
        display = "None"
    elif val == True:
        display = "是"
    elif val == False:
        display = "否"
    else:
        display = str(val)
    print(f"  teacher_id={row[0]}, 是否独生子女={display}")

cursor.close()
conn.close()
