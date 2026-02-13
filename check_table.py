#!/usr/bin/env python3
"""检查teacher_education_record表结构"""

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
    
    # 获取表结构
    cursor.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'teacher_education_record'
        ORDER BY ordinal_position
    """)
    
    columns = cursor.fetchall()
    print("teacher_education_record表的字段:")
    for col in columns:
        print(f"  - {col[0]}")
    
    cursor.close()
    conn.close()
except Exception as e:
    print(f"Error: {e}")
