#!/usr/bin/env python3
"""
检查导入日志和后端输出
"""

import psycopg2
import os
from datetime import datetime

# 数据库连接参数
DB_PARAMS = {
    'host': 'localhost',
    'database': 'taiping_education',
    'user': 'taiping_user',
    'password': 'taiping_password'
}

def get_all_tables_with_data():
    """获取所有有数据的表"""
    conn = psycopg2.connect(**DB_PARAMS)
    cursor = conn.cursor()
    
    # 获取所有表
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name
    """)
    tables = cursor.fetchall()
    
    tables_with_data = []
    for (table_name,) in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        if count > 0:
            # 获取最新的一条数据
            cursor.execute(f"SELECT * FROM {table_name} ORDER BY id DESC LIMIT 1")
            row = cursor.fetchone()
            col_names = [desc[0] for desc in cursor.description]
            tables_with_data.append({
                'name': table_name,
                'count': count,
                'latest': dict(zip(col_names, row)) if row else None
            })
    
    cursor.close()
    conn.close()
    
    return tables_with_data

if __name__ == "__main__":
    print("检查所有有数据的表...")
    print("=" * 80)
    
    tables = get_all_tables_with_data()
    
    for table in tables:
        print(f"\n表名: {table['name']}")
        print(f"记录数: {table['count']}")
        if table['latest']:
            print(f"最新记录: {table['latest']}")
        print("-" * 80)
