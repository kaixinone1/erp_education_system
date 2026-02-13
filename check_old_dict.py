#!/usr/bin/env python3
"""
检查旧字典表结构
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
            WHERE table_name = 'dict_teacher_position_dictionary'
        )
    """)
    exists = cursor.fetchone()[0]
    print(f"字典表存在: {exists}")
    
    if exists:
        # 查看表结构
        print("\n表结构:")
        cursor.execute("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = 'dict_teacher_position_dictionary'
            ORDER BY ordinal_position
        """)
        for row in cursor.fetchall():
            print(f"  {row[0]}: {row[1]}")
        
        # 查看数据
        print("\n表数据:")
        cursor.execute("SELECT * FROM dict_teacher_position_dictionary")
        for row in cursor.fetchall():
            print(f"  {row}")
finally:
    cursor.close()
    conn.close()
