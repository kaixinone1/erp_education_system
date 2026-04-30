#!/usr/bin/env python3
"""列出系统中所有表及其中文映射"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import json
import os

def list_tables():
    conn_params = {
        'host': 'localhost',
        'port': 5432,
        'database': 'taiping_education',
        'user': 'taiping_user',
        'password': 'taiping_password'
    }
    
    try:
        conn = psycopg2.connect(**conn_params)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # 查询所有表
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        
        tables = cursor.fetchall()
        
        print("系统中所有表：")
        print("=" * 80)
        
        for table in tables:
            table_name = table[0]
            
            # 查询表注释
            cursor.execute("""
                SELECT obj_description(%s::regclass, 'pg_class')
            """, (table_name,))
            comment = cursor.fetchone()[0]
            
            print(f"\n表名: {table_name}")
            if comment:
                print(f"  注释: {comment}")
            
            # 查询字段
            cursor.execute("""
                SELECT column_name, data_type,
                       col_description(%s::regclass, ordinal_position) as col_comment
                FROM information_schema.columns 
                WHERE table_name = %s
                ORDER BY ordinal_position
            """, (table_name, table_name))
            
            columns = cursor.fetchall()
            print(f"  字段数: {len(columns)}")
            for col in columns[:5]:  # 只显示前5个字段
                col_comment = col[2] if col[2] else "无注释"
                print(f"    - {col[0]} ({col[1]}) - {col_comment}")
            if len(columns) > 5:
                print(f"    ... 还有 {len(columns)-5} 个字段")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"[ERROR] {e}")

if __name__ == '__main__':
    list_tables()
