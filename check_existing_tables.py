#!/usr/bin/env python3
"""
检查现有的教师相关表
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
    # 1. 查看所有表
    print("1. 所有表:")
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name
    """)
    tables = [row[0] for row in cursor.fetchall()]
    for table in tables:
        print(f"   {table}")
    
    # 2. 查找教师人才类型表
    print("\n2. 查找教师人才类型相关表:")
    for table in tables:
        if 'talent' in table.lower() or '人才' in table:
            print(f"   {table}")
    
    # 3. 查看 teacher_talent_type 表（如果存在）
    if 'teacher_talent_type' in tables:
        print("\n3. teacher_talent_type 表结构:")
        cursor.execute("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = 'teacher_talent_type'
            ORDER BY ordinal_position
        """)
        for row in cursor.fetchall():
            print(f"   {row[0]}: {row[1]}")
        
        print("\n4. teacher_talent_type 数据样本:")
        cursor.execute("SELECT * FROM teacher_talent_type LIMIT 5")
        columns = [desc[0] for desc in cursor.description]
        print(f"   字段: {columns}")
        for row in cursor.fetchall():
            print(f"   {row}")
    else:
        print("\n   teacher_talent_type 表不存在！")
        
        # 查找可能的人才类型表
        print("\n5. 可能的人才类型表:")
        for table in tables:
            cursor.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table}'")
            columns = [row[0] for row in cursor.fetchall()]
            if any('人才' in col or 'talent' in col.lower() for col in columns):
                print(f"   {table}: {columns}")
    
finally:
    cursor.close()
    conn.close()
