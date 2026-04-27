#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查数据库中教师相关的表"""

import sys
sys.path.append('d:\\erp_thirteen\\tp_education_system\\backend')

from database.db_config import get_db_connection

def check_teacher_tables():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 查询所有教师相关的表
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema='public' 
        AND (table_name LIKE '%teacher%' 
             OR table_name LIKE '%岗位%'
             OR table_name LIKE '%聘任%'
             OR table_name LIKE '%资格%'
             OR table_name LIKE '%职称%'
             OR table_name LIKE '%performance%'
             OR table_name LIKE '%position%')
        ORDER BY table_name
    """)
    
    tables = cursor.fetchall()
    print('=' * 60)
    print('数据库中教师相关的表：')
    print('=' * 60)
    for t in tables:
        print(f'  - {t[0]}')
    
    # 查询所有表
    print('\n' + '=' * 60)
    print('数据库中所有表：')
    print('=' * 60)
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema='public'
        ORDER BY table_name
    """)
    all_tables = cursor.fetchall()
    for t in all_tables:
        print(f'  - {t[0]}')
    
    cursor.close()
    conn.close()

if __name__ == '__main__':
    check_teacher_tables()
