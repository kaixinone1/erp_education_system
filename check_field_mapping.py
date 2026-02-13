#!/usr/bin/env python3
"""
检查字段映射问题
"""

import psycopg2
import json

# 数据库连接参数
DB_PARAMS = {
    'host': 'localhost',
    'database': 'taiping_education',
    'user': 'taiping_user',
    'password': 'taiping_password'
}

def check_table_structure(table_name):
    """检查表结构"""
    conn = psycopg2.connect(**DB_PARAMS)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = %s
        ORDER BY ordinal_position
    """, (table_name,))
    
    columns = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return columns

if __name__ == "__main__":
    print("检查teacher_record表结构:")
    print("=" * 60)
    
    columns = check_table_structure('teacher_record')
    
    print(f"{'字段名':<20} {'数据类型':<20}")
    print("-" * 60)
    
    for col_name, data_type in columns:
        print(f"{col_name:<20} {data_type:<20}")
    
    print("\n" + "=" * 60)
    print("\n可能的问题:")
    print("1. 如果导入文件中的字段名与表字段名不匹配，数据将无法插入")
    print("2. 检查导入文件的字段名是否与上述字段名一致")
    print("3. 特别注意：中文字段名必须完全匹配（包括空格、特殊字符）")
