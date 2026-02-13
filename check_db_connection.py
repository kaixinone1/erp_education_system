#!/usr/bin/env python3
"""检查API使用的数据库连接"""
import psycopg2

# 与API相同的配置
def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        port="5432",
        database="taiping_education",
        user="taiping_user",
        password="taiping_password"
    )

def check():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 检查当前数据库
    cursor.execute("SELECT current_database()")
    print(f"当前数据库: {cursor.fetchone()[0]}")
    
    # 检查教师数量
    cursor.execute("SELECT COUNT(*) FROM teacher_basic_info")
    print(f"教师总数: {cursor.fetchone()[0]}")
    
    # 搜索王军锋
    name = "王军锋"
    cursor.execute("SELECT id, name FROM teacher_basic_info WHERE name LIKE %s", (f"%{name}%",))
    rows = cursor.fetchall()
    print(f"搜索'{name}'结果: {len(rows)}条")
    for row in rows:
        print(f"  {row}")
    
    # 检查ID为273的教师
    cursor.execute("SELECT id, name FROM teacher_basic_info WHERE id = 273")
    row = cursor.fetchone()
    if row:
        print(f"\nID 273的教师: {row}")
    else:
        print("\nID 273的教师不存在")
    
    cursor.close()
    conn.close()

if __name__ == '__main__':
    check()
