#!/usr/bin/env python3
"""测试正确的名字"""
import psycopg2

DATABASE_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "database": "taiping_education",
    "user": "taiping_user",
    "password": "taiping_password"
}

def test():
    conn = psycopg2.connect(**DATABASE_CONFIG)
    cursor = conn.cursor()
    
    # 测试王军锋（错误的）
    cursor.execute("SELECT id, name FROM teacher_basic_info WHERE name LIKE '%王军锋%'")
    rows = cursor.fetchall()
    print(f"搜索'王军锋'（错误的）: {len(rows)}条")
    
    # 测试王军峰（正确的）
    cursor.execute("SELECT id, name FROM teacher_basic_info WHERE name LIKE '%王军峰%'")
    rows = cursor.fetchall()
    print(f"搜索'王军峰'（正确的）: {len(rows)}条")
    for row in rows:
        print(f"  ID:{row[0]}, 姓名:{row[1]}")
    
    cursor.close()
    conn.close()

if __name__ == '__main__':
    test()
