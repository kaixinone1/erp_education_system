#!/usr/bin/env python3
"""检查教师数据"""
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
    
    # 搜索王军锋
    cursor.execute("SELECT id, name, id_card FROM teacher_basic_info WHERE name LIKE '%王军锋%'")
    rows = cursor.fetchall()
    print(f"搜索'王军锋'结果: {len(rows)}条")
    for row in rows:
        print(f"  ID: {row[0]}, 姓名: {row[1]}, 身份证: {row[2]}")
    
    # 查看所有教师姓名
    cursor.execute("SELECT name FROM teacher_basic_info LIMIT 10")
    rows = cursor.fetchall()
    print("\n前10个教师姓名:")
    for row in rows:
        print(f"  {row[0]}")
    
    cursor.close()
    conn.close()

if __name__ == '__main__':
    check()
