#!/usr/bin/env python3
"""检查字典表是否存在"""
import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port=5432,
    database='taiping_education',
    user='taiping_user',
    password='taiping_password'
)
cursor = conn.cursor()

# 检查字典表
dict_tables = [
    'dict_education_type_dictionary',
    'dict_education_level_dictionary',
    'dict_education_dictionary'
]

print("检查字典表:")
for table in dict_tables:
    cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = %s
        )
    """, (table,))
    exists = cursor.fetchone()[0]
    print(f"  - {table}: {'存在' if exists else '不存在'}")
    
    if exists:
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = %s 
            ORDER BY ordinal_position
        """, (table,))
        columns = [row[0] for row in cursor.fetchall()]
        print(f"    列: {columns}")

cursor.close()
conn.close()
