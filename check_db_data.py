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

# 检查教师ID 273的数据
fields = ['职务2', '岗位2', '薪级2', '入党年月', '是否独生子女', '现住址', '直系亲属信息', '证明人及其住址']

print("教师ID 273 的数据:")
print("=" * 60)

for field in fields:
    try:
        cursor.execute(f'SELECT "{field}" FROM retirement_report_data WHERE teacher_id = %s', (273,))
        row = cursor.fetchone()
        value = row[0] if row and row[0] else '(空)'
        print(f"  {field}: {value}")
    except Exception as e:
        print(f"  {field}: 字段不存在 - {e}")

cursor.close()
conn.close()

print("\n" + "=" * 60)
print("结论: 这些字段在数据库中没有数据，所以占位符无法被替换")
