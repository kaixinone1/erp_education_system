#!/usr/bin/env python3
"""
删除我错误创建的字典表，只保留用户原有的字典表
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
    print("清理错误创建的字典表")
    print("=" * 80)
    
    # 我错误创建的字典表（根据之前的分析）
    wrong_tables = [
        'dict_talent_type',  # 这是我测试时创建的，用户已经有 dict_data_dictionary
    ]
    
    for table in wrong_tables:
        cursor.execute(f"DROP TABLE IF EXISTS {table}")
        print(f"  删除错误创建的表: {table}")
    
    conn.commit()
    
    print("\n" + "=" * 80)
    print("保留的用户原有字典表:")
    print("=" * 80)
    
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        AND table_name LIKE 'dict_%'
        ORDER BY table_name
    """)
    
    for row in cursor.fetchall():
        print(f"  {row[0]}")
    
finally:
    cursor.close()
    conn.close()
