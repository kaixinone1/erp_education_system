#!/usr/bin/env python3
"""验证 teacher_education_record 表的 teacher_id 填充"""
import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port='5432',
    database='taiping_education',
    user='taiping_user',
    password='taiping_password'
)
cursor = conn.cursor()

# 检查 teacher_id 为 NULL 的记录数
cursor.execute('SELECT COUNT(*) FROM teacher_education_record WHERE teacher_id IS NULL')
null_count = cursor.fetchone()[0]
print(f"teacher_id 为 NULL 的记录数: {null_count}")

# 检查 teacher_id 已填充的记录数
cursor.execute('SELECT COUNT(*) FROM teacher_education_record WHERE teacher_id IS NOT NULL')
filled_count = cursor.fetchone()[0]
print(f"teacher_id 已填充的记录数: {filled_count}")

# 显示几条示例数据
cursor.execute('''
    SELECT ter.id, ter.teacher_id, ter.id_card, ter.education, tbi.name
    FROM teacher_education_record ter
    JOIN teacher_basic_info tbi ON ter.teacher_id = tbi.id
    LIMIT 5
''')
print("\n示例数据（前5条）:")
for row in cursor.fetchall():
    print(f"  id={row[0]}, teacher_id={row[1]}, id_card={row[2]}, education={row[3]}, name={row[4]}")

cursor.close()
conn.close()
