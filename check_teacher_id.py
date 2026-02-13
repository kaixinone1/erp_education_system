#!/usr/bin/env python3
"""检查todo_work_items表中的teacher_id数据"""

import psycopg2

def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        port="5432",
        database="taiping_education",
        user="taiping_user",
        password="taiping_password"
    )

try:
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 查看所有待办任务的教师ID
    cursor.execute("""
        SELECT id, 教师id, 教师姓名, 清单名称 
        FROM todo_work_items 
        ORDER BY id
    """)
    
    rows = cursor.fetchall()
    print("所有待办任务的教师ID:")
    for row in rows:
        teacher_id = row[1]
        print(f"  ID: {row[0]}, 教师ID: {teacher_id} (类型: {type(teacher_id).__name__}), 教师姓名: {row[2]}, 清单: {row[3]}")
        
        # 检查teacher_id是否有效
        if teacher_id is None:
            print(f"    ⚠️ 警告: 教师ID为 NULL")
        elif teacher_id == 0:
            print(f"    ⚠️ 警告: 教师ID为 0")
        elif isinstance(teacher_id, str) and not teacher_id.isdigit():
            print(f"    ⚠️ 警告: 教师ID为字符串且不是数字: '{teacher_id}'")
    
    cursor.close()
    conn.close()
except Exception as e:
    print(f"Error: {e}")
