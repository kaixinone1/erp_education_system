#!/usr/bin/env python3
"""
检查导入历史和所有相关表的数据
"""

import psycopg2

DB_PARAMS = {
    'host': 'localhost',
    'database': 'taiping_education',
    'user': 'taiping_user',
    'password': 'taiping_password'
}

def check_all():
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cursor = conn.cursor()
        
        # 1. 检查所有表
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name
        """)
        tables = [row[0] for row in cursor.fetchall()]
        
        print("数据库中的所有表:")
        for t in tables:
            print(f"  - {t}")
        
        # 2. 检查 teacher_record 表的数据量
        cursor.execute("SELECT COUNT(*) FROM teacher_record")
        count = cursor.fetchone()[0]
        print(f"\nteacher_record 表: {count} 条数据")
        
        # 3. 检查 teacher_basic 表的数据量
        cursor.execute("SELECT COUNT(*) FROM teacher_basic")
        count = cursor.fetchone()[0]
        print(f"teacher_basic 表: {count} 条数据")
        
        # 4. 检查是否有其他相关表
        teacher_tables = [t for t in tables if 'teacher' in t.lower()]
        print(f"\n教师相关表 ({len(teacher_tables)} 个):")
        for t in teacher_tables:
            cursor.execute(f"SELECT COUNT(*) FROM {t}")
            count = cursor.fetchone()[0]
            print(f"  - {t}: {count} 条数据")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"错误: {e}")

if __name__ == "__main__":
    check_all()
