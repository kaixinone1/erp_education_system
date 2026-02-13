#!/usr/bin/env python3
"""
检查 teacher_basic 表的结构
"""

import psycopg2

DB_PARAMS = {
    'host': 'localhost',
    'database': 'taiping_education',
    'user': 'taiping_user',
    'password': 'taiping_password'
}

def check_table():
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cursor = conn.cursor()
        
        # 查询表结构
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'teacher_basic' AND table_schema = 'public'
            ORDER BY ordinal_position
        """)
        
        columns = cursor.fetchall()
        print("teacher_basic 表结构:")
        print("-" * 60)
        for col_name, data_type in columns:
            print(f"  {col_name}: {data_type}")
        
        # 查询前3条数据
        cursor.execute("SELECT * FROM teacher_basic LIMIT 3")
        rows = cursor.fetchall()
        
        print("\n前3条数据:")
        print("-" * 60)
        col_names = [desc[0] for desc in cursor.description]
        print(f"列名: {col_names}")
        for row in rows:
            print(f"  {row}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"错误: {e}")

if __name__ == "__main__":
    check_table()
