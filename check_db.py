#!/usr/bin/env python3
"""检查数据库表结构"""
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
    
    # 检查document_templates表
    cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'document_templates'
        )
    """)
    if cursor.fetchone()[0]:
        print("✓ document_templates 表存在")
        
        # 检查表结构
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'document_templates'
            ORDER BY ordinal_position
        """)
        print("  列:")
        for row in cursor.fetchall():
            print(f"    - {row[0]}: {row[1]}")
    else:
        print("✗ document_templates 表不存在")
    
    # 检查template_field_mappings表
    cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'template_field_mappings'
        )
    """)
    if cursor.fetchone()[0]:
        print("\n✓ template_field_mappings 表存在")
    else:
        print("\n✗ template_field_mappings 表不存在")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    check_db()
