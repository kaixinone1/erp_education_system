#!/usr/bin/env python3
"""检查身份证号"""
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
    
    # 检查身份证号
    cursor.execute("SELECT id, name, id_card FROM teacher_basic_info WHERE id_card = '420683196909152209'")
    row = cursor.fetchone()
    if row:
        print(f"找到该身份证: ID={row[0]}, 姓名={row[1]}, 身份证={row[2]}")
    else:
        print("未找到该身份证")
    
    cursor.close()
    conn.close()

if __name__ == '__main__':
    check()
