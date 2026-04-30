#!/usr/bin/env python3
"""执行SQL文件创建数据库表结构"""

import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def execute_sql_file():
    """执行SQL文件"""
    # 数据库连接信息
    conn_params = {
        'host': 'localhost',
        'port': 5432,
        'database': 'taiping_education',
        'user': 'taiping_user',
        'password': 'taiping_password'
    }
    
    try:
        # 连接数据库
        conn = psycopg2.connect(**conn_params)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # 获取SQL文件路径
        current_dir = os.path.dirname(os.path.abspath(__file__))
        sql_file = os.path.join(current_dir, 'create_report_template_tables.sql')
        
        # 读取SQL文件
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # 执行SQL
        cursor.execute(sql_content)
        
        print("[OK] 数据库表创建成功！")
        
        # 验证表是否创建成功
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN (
                'report_templates',
                'report_template_fields',
                'report_field_sources',
                'report_tag_filters',
                'report_calculate_fields',
                'report_data_remarks',
                'report_generation_logs',
                'performance_salary_standard'
            )
            ORDER BY table_name
        """)
        
        tables = cursor.fetchall()
        print("\n已创建的表:")
        for table in tables:
            print("  - " + table[0])
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print("[ERROR] 执行失败: " + str(e))
        return False
    
    return True

if __name__ == '__main__':
    execute_sql_file()
