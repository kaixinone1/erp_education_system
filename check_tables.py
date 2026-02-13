#!/usr/bin/env python3
"""检查数据库表"""
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
    
    # 查看所有表
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        ORDER BY table_name
    """)
    
    tables = cursor.fetchall()
    print("数据库中的表:")
    for table in tables:
        print(f"  - {table[0]}")
    
    # 查找todo相关的表
    print("\n查找todo相关的表:")
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name LIKE '%todo%'
        ORDER BY table_name
    """)
    
    todo_tables = cursor.fetchall()
    if todo_tables:
        for table in todo_tables:
            print(f"  - {table[0]}")
    else:
        print("  没有找到todo相关的表")
    
    cursor.close()
    conn.close()

if __name__ == '__main__':
    check()
