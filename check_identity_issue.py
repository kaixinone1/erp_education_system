#!/usr/bin/env python3
"""
检查个人身份字段的关联问题
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
    # 1. 查看有哪些表
    print("=" * 80)
    print("1. 数据库中的表")
    print("=" * 80)
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name
    """)
    tables = [row[0] for row in cursor.fetchall()]
    for table in tables:
        print(f"  {table}")
    
    # 2. 查找包含"身份"的表
    print("\n" + "=" * 80)
    print("2. 包含'身份'的表")
    print("=" * 80)
    identity_tables = [t for t in tables if '身份' in t or 'identity' in t.lower()]
    print(f"  {identity_tables}")
    
    # 3. 查看 teacher_basic 表结构
    print("\n" + "=" * 80)
    print("3. teacher_basic 表结构")
    print("=" * 80)
    cursor.execute("""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = 'teacher_basic'
        ORDER BY ordinal_position
    """)
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]}")
    
    # 4. 查看 teacher_basic 数据样本
    print("\n" + "=" * 80)
    print("4. teacher_basic 数据样本（前5条）")
    print("=" * 80)
    cursor.execute("""
        SELECT * FROM teacher_basic 
        LIMIT 5
    """)
    columns = [desc[0] for desc in cursor.description]
    print(f"  字段: {columns}")
    for row in cursor.fetchall():
        print(f"  {row}")
    
    # 5. 查找字典表
    print("\n" + "=" * 80)
    print("5. 字典表")
    print("=" * 80)
    dict_tables = [t for t in tables if t.startswith('dict_')]
    for table in dict_tables:
        print(f"  {table}")
    
    # 6. 查看 dict_identity 或类似表
    identity_dict_tables = [t for t in dict_tables if 'identity' in t.lower() or '身份' in t]
    print(f"\n  身份相关字典表: {identity_dict_tables}")
    
    if identity_dict_tables:
        for table in identity_dict_tables:
            print(f"\n  {table} 表结构:")
            cursor.execute(f"""
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_name = '{table}'
                ORDER BY ordinal_position
            """)
            for row in cursor.fetchall():
                print(f"    {row[0]}: {row[1]}")
            
            print(f"\n  {table} 数据:")
            cursor.execute(f"SELECT * FROM {table}")
            for row in cursor.fetchall():
                print(f"    {row}")
    
    # 7. 查看哪个子表包含"个人身份"字段
    print("\n" + "=" * 80)
    print("7. 查找包含'个人身份'字段的表")
    print("=" * 80)
    cursor.execute("""
        SELECT table_name, column_name
        FROM information_schema.columns
        WHERE column_name LIKE '%身份%' OR column_name LIKE '%identity%'
        ORDER BY table_name
    """)
    for row in cursor.fetchall():
        print(f"  表: {row[0]}, 字段: {row[1]}")
    
    # 8. 查看具体子表的数据
    print("\n" + "=" * 80)
    print("8. 检查子表数据")
    print("=" * 80)
    
    # 先找到包含个人身份的子表
    cursor.execute("""
        SELECT DISTINCT table_name
        FROM information_schema.columns
        WHERE column_name LIKE '%个人身份%' OR column_name LIKE '%identity%'
    """)
    sub_tables = [row[0] for row in cursor.fetchall()]
    
    for table in sub_tables:
        if table != 'teacher_basic':
            print(f"\n  {table} 表:")
            cursor.execute(f"""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = '{table}'
                ORDER BY ordinal_position
            """)
            columns = [row[0] for row in cursor.fetchall()]
            print(f"    字段: {columns}")
            
            # 查找身份相关的字段
            identity_cols = [c for c in columns if '身份' in c or 'identity' in c.lower()]
            print(f"    身份字段: {identity_cols}")
            
            # 查看数据样本
            if identity_cols:
                cursor.execute(f"SELECT * FROM {table} LIMIT 3")
                rows = cursor.fetchall()
                print(f"    数据样本:")
                for row in rows:
                    print(f"      {row}")

finally:
    cursor.close()
    conn.close()
