#!/usr/bin/env python3
"""检查状态字段值"""
import psycopg2

DATABASE_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "database": "taiping_education",
    "user": "taiping_user",
    "password": "taiping_password"
}

def check():
    conn = psycopg2.connect(**DATABASE_CONFIG)
    cursor = conn.cursor()
    
    # 查询状态字段
    cursor.execute("""
        SELECT id, 教师姓名, 状态
        FROM todo_work_items
    """)
    
    rows = cursor.fetchall()
    for row in rows:
        print(f"ID: {row[0]}, 姓名: {row[1]}, 状态: '{row[2]}'")
    
    cursor.close()
    conn.close()

if __name__ == '__main__':
    check()
