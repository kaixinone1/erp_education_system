#!/usr/bin/env python3
"""
检查教师个人身份表数据
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
    # 1. 检查表是否存在
    print("1. 检查 teacher_personal_identity 表是否存在...")
    cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'teacher_personal_identity'
        )
    """)
    exists = cursor.fetchone()[0]
    print(f"   表存在: {exists}")
    
    if not exists:
        print("   表不存在！")
        # 查看有哪些表
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            AND table_name LIKE '%personal%'
        """)
        tables = [row[0] for row in cursor.fetchall()]
        print(f"   相关表: {tables}")
    else:
        # 2. 查看表结构
        print("\n2. 表结构:")
        cursor.execute("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = 'teacher_personal_identity'
            ORDER BY ordinal_position
        """)
        for row in cursor.fetchall():
            print(f"   {row[0]}: {row[1]}")
        
        # 3. 查看数据条数
        print("\n3. 数据条数:")
        cursor.execute("SELECT COUNT(*) FROM teacher_personal_identity")
        count = cursor.fetchone()[0]
        print(f"   共 {count} 条记录")
        
        # 4. 查看前5条数据
        if count > 0:
            print("\n4. 前5条数据:")
            cursor.execute("SELECT * FROM teacher_personal_identity LIMIT 5")
            columns = [desc[0] for desc in cursor.description]
            print(f"   字段: {columns}")
            for row in cursor.fetchall():
                print(f"   {row}")
        else:
            print("\n4. 表中没有数据！")
            
            # 检查是否有其他相关表
            print("\n5. 查找包含'personal_identity'的表:")
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                AND (table_name LIKE '%personal%' OR table_name LIKE '%identity%')
            """)
            tables = [row[0] for row in cursor.fetchall()]
            print(f"   相关表: {tables}")
            
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"   {table}: {count} 条记录")
    
finally:
    cursor.close()
    conn.close()
