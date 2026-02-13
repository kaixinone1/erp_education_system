#!/usr/bin/env python3
"""
验证导入的数据
"""

import psycopg2

DB_PARAMS = {
    'host': 'localhost',
    'database': 'taiping_education',
    'user': 'taiping_user',
    'password': 'taiping_password'
}

def verify():
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cursor = conn.cursor()
        
        # 查询 teacher_record 表的数据
        cursor.execute("SELECT * FROM teacher_record")
        rows = cursor.fetchall()
        
        print(f"teacher_record 表中有 {len(rows)} 条数据")
        print("-" * 60)
        
        if rows:
            col_names = [desc[0] for desc in cursor.description]
            print(f"列名: {col_names}")
            print()
            
            for i, row in enumerate(rows, 1):
                print(f"第 {i} 条数据:")
                for col, val in zip(col_names, row):
                    print(f"  {col}: {val}")
                print()
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"错误: {e}")

if __name__ == "__main__":
    verify()
