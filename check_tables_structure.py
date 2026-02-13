#!/usr/bin/env python3
"""
检查没有中文映射的表结构
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

# 没有中文映射的表
unmapped_tables = [
    'dict_education_dictionary',
    'dict_position',
    'education_dictionary',
    'teacher_basic',
    'test_import_table'
]

for table in unmapped_tables:
    print("=" * 80)
    print(f"表: {table}")
    print("=" * 80)
    
    cursor.execute("""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = %s AND table_schema = 'public'
        ORDER BY ordinal_position
    """, (table,))
    
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]}")
    print()

cursor.close()
conn.close()
