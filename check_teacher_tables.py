#!/usr/bin/env python3
"""检查教师相关表的结构"""

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
        AND table_name LIKE '%teacher%'
        ORDER BY table_name
    """)
    
    tables = cursor.fetchall()
    print("教师相关表:")
    for table in tables:
        print(f"\n  - {table[0]}")
        
        # 获取表结构
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = %s
            ORDER BY ordinal_position
        """, (table[0],))
        
        columns = cursor.fetchall()
        for col in columns:
            print(f"      {col[0]}: {col[1]}")
    
    cursor.close()
    conn.close()
except Exception as e:
    print(f"Error: {e}")
