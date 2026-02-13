#!/usr/bin/env python3
"""
检查teacher_log表的结构和数据
"""

import psycopg2

# 数据库连接参数
DB_PARAMS = {
    'host': 'localhost',
    'database': 'taiping_education',
    'user': 'taiping_user',
    'password': 'taiping_password'
}

def check_table_structure(table_name):
    """检查表结构"""
    print(f"检查{table_name}表的结构...")
    
    conn = psycopg2.connect(**DB_PARAMS)
    cursor = conn.cursor()
    
    # 查询表结构
    cursor.execute("""
        SELECT column_name, data_type, character_maximum_length 
        FROM information_schema.columns 
        WHERE table_name = %s
        ORDER BY ordinal_position
    """, (table_name,))
    
    print(f"\n{table_name}表结构:")
    print("-" * 60)
    print(f"{'字段名':<20} {'数据类型':<20} {'长度':<10}")
    print("-" * 60)
    
    for row in cursor.fetchall():
        column_name, data_type, max_length = row
        length = max_length if max_length else "-"
        print(f"{column_name:<20} {data_type:<20} {length:<10}")
    
    # 查询数据
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    print(f"\n记录数: {count}")
    
    if count > 0:
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
        rows = cursor.fetchall()
        col_names = [desc[0] for desc in cursor.description]
        
        print("\n前5条数据:")
        print("-" * 60)
        for i, row in enumerate(rows, 1):
            print(f"{i}. {dict(zip(col_names, row))}")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    check_table_structure('teacher_record')
    print("\n" + "=" * 60 + "\n")
    check_table_structure('teacher_log')
