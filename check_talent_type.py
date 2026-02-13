#!/usr/bin/env python3
"""
检查人才类型表的数据
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
    # 1. 查看有哪些表包含"talent"
    print("1. 查看相关表:")
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        AND (table_name LIKE '%talent%' OR table_name LIKE '%人才%')
    """)
    tables = [row[0] for row in cursor.fetchall()]
    print(f"   相关表: {tables}")
    
    # 2. 查看教师人才类型表结构
    if 'teacher_talent_type' in tables:
        print("\n2. teacher_talent_type 表结构:")
        cursor.execute("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = 'teacher_talent_type'
            ORDER BY ordinal_position
        """)
        for row in cursor.fetchall():
            print(f"   {row[0]}: {row[1]}")
        
        # 3. 查看数据样本
        print("\n3. teacher_talent_type 数据样本:")
        cursor.execute("SELECT * FROM teacher_talent_type LIMIT 5")
        columns = [desc[0] for desc in cursor.description]
        print(f"   字段: {columns}")
        for row in cursor.fetchall():
            print(f"   {row}")
    
    # 4. 查看字典表
    print("\n4. 查看 dict_talent_type 字典表:")
    cursor.execute("SELECT * FROM dict_talent_type")
    for row in cursor.fetchall():
        print(f"   {row}")
    
finally:
    cursor.close()
    conn.close()
