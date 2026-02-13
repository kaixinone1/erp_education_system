#!/usr/bin/env python3
"""检查todo_work_items表"""
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
    
    # 查看表结构
    print("=== todo_work_items 表结构 ===")
    cursor.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'todo_work_items'
        ORDER BY ordinal_position
    """)
    
    columns = cursor.fetchall()
    for col in columns:
        print(f"  {col[0]}: {col[1]}")
    
    # 查看数据
    print("\n=== todo_work_items 数据 ===")
    cursor.execute("SELECT * FROM todo_work_items ORDER BY id DESC LIMIT 10")
    
    rows = cursor.fetchall()
    print(f"记录数: {len(rows)}")
    
    if rows:
        col_names = [desc[0] for desc in cursor.description]
        print(f"列名: {col_names}")
        for row in rows:
            print(f"  {row}")
    else:
        print("  表中没有数据")
    
    cursor.close()
    conn.close()

if __name__ == '__main__':
    check()
