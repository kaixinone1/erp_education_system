#!/usr/bin/env python3
"""检查所有表的结构"""

import psycopg2

def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        port="5432",
        database="taiping_education",
        user="taiping_user",
        password="taiping_password"
    )

try:
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 获取所有表名
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_type = 'BASE TABLE'
        ORDER BY table_name
    """)
    
    tables = cursor.fetchall()
    print("所有表:")
    for table in tables:
        print(f"  - {table[0]}")
    
    cursor.close()
    conn.close()
except Exception as e:
    print(f"Error: {e}")
