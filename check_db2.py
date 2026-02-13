#!/usr/bin/env python3
"""检查template_field_mappings表结构"""
import psycopg2

def check_db():
    conn = psycopg2.connect(
        host="localhost",
        port="5432",
        database="taiping_education",
        user="taiping_user",
        password="taiping_password"
    )
    cursor = conn.cursor()
    
    # 检查template_field_mappings表结构
    cursor.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'template_field_mappings'
        ORDER BY ordinal_position
    """)
    print("template_field_mappings 表结构:")
    for row in cursor.fetchall():
        print(f"  - {row[0]}: {row[1]}")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    check_db()
