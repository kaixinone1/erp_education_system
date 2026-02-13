#!/usr/bin/env python3
"""
检查 teacher_record 表中的真实数据
"""

import psycopg2

DB_PARAMS = {
    'host': 'localhost',
    'database': 'taiping_education',
    'user': 'taiping_user',
    'password': 'taiping_password'
}

def check_data():
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cursor = conn.cursor()
        
        # 查询所有数据
        cursor.execute("SELECT * FROM teacher_record ORDER BY id")
        rows = cursor.fetchall()
        
        # 获取列名
        col_names = [desc[0] for desc in cursor.description]
        
        print(f"teacher_record 表共有 {len(rows)} 条数据")
        print("=" * 80)
        
        for i, row in enumerate(rows, 1):
            print(f"\n第 {i} 条数据:")
            for col, val in zip(col_names, row):
                if val:  # 只显示非空值
                    print(f"  {col}: {val}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"错误: {e}")

if __name__ == "__main__":
    check_data()
