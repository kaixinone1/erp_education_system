#!/usr/bin/env python3
"""
验证导入数据的来源 - 检查是否是通过V3服务导入的
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
    print("=" * 80)
    print("验证数据库中的表结构和数据")
    print("=" * 80)
    
    # 1. 查看所有表
    print("\n1. 当前数据库中的所有表:")
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name
    """)
    tables = [row[0] for row in cursor.fetchall()]
    for table in tables:
        print(f"   {table}")
    
    # 2. 检查 teacher_talent_type 表是否存在
    if 'teacher_talent_type' in tables:
        print("\n2. teacher_talent_type 表结构:")
        cursor.execute("""
            SELECT column_name, data_type, ordinal_position
            FROM information_schema.columns
            WHERE table_name = 'teacher_talent_type'
            ORDER BY ordinal_position
        """)
        columns = cursor.fetchall()
        for col in columns:
            print(f"   {col[0]}: {col[1]}")
        
        # 检查是否有 talent_type_id, talent_type_name 字段（V3服务创建的）
        has_v3_fields = any(col[0] in ['talent_type_id', 'talent_type_name', 'talent_type_code'] for col in columns)
        
        if has_v3_fields:
            print("\n   ✅ 这是V3服务创建的表（有字典关联字段）")
            
            print("\n3. teacher_talent_type 数据样本:")
            cursor.execute("""
                SELECT name, id_card, talent_type_id, talent_type_name, talent_type_code
                FROM teacher_talent_type
                LIMIT 5
            """)
            for row in cursor.fetchall():
                print(f"   姓名: {row[0]}, 人才类型: {row[3]} (id={row[2]}, code={row[4]})")
        else:
            print("\n   ⚠️ 这是旧版导入创建的表（没有字典关联字段）")
            
            print("\n3. 数据样本:")
            cursor.execute("SELECT * FROM teacher_talent_type LIMIT 3")
            columns = [desc[0] for desc in cursor.description]
            print(f"   字段: {columns}")
            for row in cursor.fetchall():
                print(f"   {row}")
    else:
        print("\n2. teacher_talent_type 表不存在！")
    
    # 4. 检查 dict_talent_type 字典表
    if 'dict_talent_type' in tables:
        print("\n4. dict_talent_type 字典表内容:")
        cursor.execute("SELECT id, code, name FROM dict_talent_type")
        for row in cursor.fetchall():
            print(f"   id={row[0]}, code={row[1]}, name={row[2]}")
    else:
        print("\n4. dict_talent_type 字典表不存在！")
    
    # 5. 检查其他可能的表
    print("\n5. 检查其他可能的人才类型相关表:")
    for table in tables:
        if 'talent' in table.lower() or '人才' in table:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"   {table}: {count} 条数据")
    
finally:
    cursor.close()
    conn.close()
