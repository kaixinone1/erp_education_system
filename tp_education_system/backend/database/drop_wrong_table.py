#!/usr/bin/env python3
"""删除错误创建的绩效工资标准表"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def drop_table():
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
        
        # 删除我创建的错误表
        cursor.execute("DROP TABLE IF EXISTS performance_salary_standard CASCADE")
        print("[OK] 已删除 performance_salary_standard 表")
        
        # 确认 dict_salary_dictionary 表存在
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'dict_salary_dictionary'
            )
        """)
        exists = cursor.fetchone()[0]
        if exists:
            print("[OK] 正确的表 dict_salary_dictionary 存在")
            
            # 查看表中的数据
            cursor.execute("SELECT 岗位, 月绩效工资标准 FROM dict_salary_dictionary LIMIT 10")
            rows = cursor.fetchall()
            print("\n正确的绩效工资标准数据（前10条）:")
            for row in rows:
                print(f"  {row[0]}: {row[1]}")
        else:
            print("[WARNING] dict_salary_dictionary 表不存在!")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"[ERROR] {e}")

if __name__ == '__main__':
    drop_table()
