#!/usr/bin/env python3
"""检查retirement_report_form表的结构"""

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
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'retirement_report_form'
        ORDER BY ordinal_position
    """)
    
    columns = cursor.fetchall()
    print("retirement_report_form 表结构:")
    for col in columns:
        print(f"  - {col[0]}: {col[1]}")
    
    # 查看示例数据
    cursor.execute("""
        SELECT * FROM retirement_report_form 
        LIMIT 1
    """)
    
    row = cursor.fetchone()
    if row:
        print("\n示例数据:")
        for i, col in enumerate(columns):
            print(f"  {col[0]}: {row[i]}")
    else:
        print("\n表中没有数据")
    
    cursor.close()
    conn.close()
except Exception as e:
    print(f"Error: {e}")
