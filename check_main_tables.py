#!/usr/bin/env python3
"""
检查主表名称
"""

import psycopg2

# 数据库连接参数
DB_PARAMS = {
    'host': 'localhost',
    'database': 'taiping_education',
    'user': 'taiping_user',
    'password': 'taiping_password'
}

def check_tables():
    """检查所有表"""
    print("检查数据库中的所有表...")
    
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cursor = conn.cursor()
        
        # 查询所有表
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        
        tables = cursor.fetchall()
        
        print(f"\n数据库中共有 {len(tables)} 个表:")
        print("-" * 60)
        
        for i, (table_name,) in enumerate(tables, 1):
            # 查询每个表的记录数
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                print(f"{i}. {table_name:<30} ({count} 条数据)")
            except:
                print(f"{i}. {table_name:<30} (无法查询)")
        
        # 查找教师相关的表
        print("\n\n教师相关的表:")
        print("-" * 60)
        for (table_name,) in tables:
            if 'teacher' in table_name.lower() or '教师' in table_name:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    count = cursor.fetchone()[0]
                    print(f"  - {table_name:<30} ({count} 条数据)")
                except:
                    print(f"  - {table_name:<30}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"错误: {e}")

if __name__ == "__main__":
    check_tables()
