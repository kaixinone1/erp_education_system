#!/usr/bin/env python3
"""
检查 teacher_log 表的数据
"""

import psycopg2

DB_PARAMS = {
    'host': 'localhost',
    'database': 'taiping_education',
    'user': 'taiping_user',
    'password': 'taiping_password'
}

conn = psycopg2.connect(**DB_PARAMS)
cursor = conn.cursor()

try:
    # 检查表是否存在
    cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'teacher_log'
        )
    """)
    exists = cursor.fetchone()[0]
    print(f"teacher_log 表存在: {exists}")
    
    if exists:
        # 查看表结构
        print("\n表结构:")
        cursor.execute("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = 'teacher_log'
            ORDER BY ordinal_position
        """)
        columns = cursor.fetchall()
        for row in columns:
            print(f"  {row[0]}: {row[1]}")
        
        # 查看数据条数
        cursor.execute("SELECT COUNT(*) FROM teacher_log")
        count = cursor.fetchone()[0]
        print(f"\n数据条数: {count}")
        
        # 查看前10条数据
        if count > 0:
            print("\n前10条数据:")
            column_names = [col[0] for col in columns]
            print(f"  字段: {column_names}")
            
            cursor.execute("SELECT * FROM teacher_log LIMIT 10")
            for i, row in enumerate(cursor.fetchall(), 1):
                print(f"  行{i}: {row}")
        else:
            print("\n表中没有数据！")
            
except Exception as e:
    print(f"查询失败: {e}")
    import traceback
    traceback.print_exc()
finally:
    cursor.close()
    conn.close()
