#!/usr/bin/env python3
"""清理数据库中的所有硬编码数据"""
import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port='5432',
    database='taiping_education',
    user='taiping_user',
    password='taiping_password'
)
cursor = conn.cursor()

# 清理 retirement_report_data 表中的硬编码数据
print("清理 retirement_report_data 表...")

# 检查哪些字段有硬编码数据
cursor.execute('''
    SELECT teacher_id, "是否独生子女", "退休原因", "职务", "岗位", "技术职称"
    FROM retirement_report_data
''')

for row in cursor.fetchall():
    teacher_id = row[0]
    is_only_child = row[1]
    retirement_reason = row[2]
    position = row[3]
    post = row[4]
    title = row[5]
    
    updates = []
    params = []
    
    # 检查是否有硬编码的值（非None且非空）
    if is_only_child is not None:
        updates.append('"是否独生子女" = NULL')
        print(f"  teacher_id={teacher_id}: 清理 是否独生子女")
    
    if retirement_reason is not None and retirement_reason != '':
        updates.append('"退休原因" = NULL')
        print(f"  teacher_id={teacher_id}: 清理 退休原因 = '{retirement_reason}'")
    
    if position is not None and position != '':
        updates.append('"职务" = NULL')
        print(f"  teacher_id={teacher_id}: 清理 职务 = '{position}'")
    
    if post is not None and post != '':
        updates.append('"岗位" = NULL')
        print(f"  teacher_id={teacher_id}: 清理 岗位 = '{post}'")
    
    if title is not None and title != '':
        updates.append('"技术职称" = NULL')
        print(f"  teacher_id={teacher_id}: 清理 技术职称 = '{title}'")
    
    if updates:
        query = f'UPDATE retirement_report_data SET {", ".join(updates)} WHERE teacher_id = %s'
        cursor.execute(query, (teacher_id,))

conn.commit()
print("\n清理完成！")

cursor.close()
conn.close()
