#!/usr/bin/env python3
"""直接测试SQL查询"""
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
    
    # 测试LIKE查询
    name = "王军锋"
    cursor.execute("SELECT id, name, id_card FROM teacher_basic_info WHERE name LIKE %s", (f"%{name}%",))
    rows = cursor.fetchall()
    print(f"LIKE查询结果: {len(rows)}条")
    for row in rows:
        print(f"  {row}")
    
    # 测试精确查询
    cursor.execute("SELECT id, name, id_card FROM teacher_basic_info WHERE name = %s", (name,))
    rows = cursor.fetchall()
    print(f"\n精确查询结果: {len(rows)}条")
    for row in rows:
        print(f"  {row}")
    
    # 查看所有教师
    cursor.execute("SELECT id, name FROM teacher_basic_info ORDER BY id DESC LIMIT 5")
    rows = cursor.fetchall()
    print(f"\n最近5条教师记录:")
    for row in rows:
        print(f"  ID:{row[0]}, 姓名:{row[1]}")
    
    cursor.close()
    conn.close()

if __name__ == '__main__':
    test()
