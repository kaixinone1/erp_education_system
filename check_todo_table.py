#!/usr/bin/env python3
"""检查todo_work_items表结构"""

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
    
    # 获取表结构
    cursor.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'todo_work_items'
        ORDER BY ordinal_position
    """)
    
    columns = cursor.fetchall()
    print("todo_work_items表的字段:")
    for col in columns:
        print(f"  - {col[0]}: {col[1]}")
    
    # 查看几条示例数据
    cursor.execute("""
        SELECT id, 教师ID, 教师姓名, 清单名称 
        FROM todo_work_items 
        LIMIT 5
    """)
    
    rows = cursor.fetchall()
    print("\n示例数据:")
    for row in rows:
        print(f"  ID: {row[0]}, 教师ID: {row[1]}, 教师姓名: {row[2]}, 清单: {row[3]}")
    
    cursor.close()
    conn.close()
except Exception as e:
    print(f"Error: {e}")
