#!/usr/bin/env python3
"""执行模板表SQL脚本"""

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
    
    # 读取SQL文件
    with open('create_template_tables.sql', 'r', encoding='utf-8') as f:
        sql = f.read()
    
    # 执行SQL
    cursor.execute(sql)
    conn.commit()
    
    print("模板表创建成功！")
    
    cursor.close()
    conn.close()
except Exception as e:
    print(f"Error: {e}")
