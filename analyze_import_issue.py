#!/usr/bin/env python3
"""
分析导入问题
"""

import psycopg2

DB_PARAMS = {
    'host': 'localhost',
    'database': 'taiping_education',
    'user': 'taiping_user',
    'password': 'taiping_password'
}

def analyze():
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cursor = conn.cursor()
        
        # 1. 检查 teacher_record 表中的所有数据
        cursor.execute("SELECT id, teacher_id, 姓名, 身份证号码 FROM teacher_record")
        rows = cursor.fetchall()
        
        print("teacher_record 表中的所有数据:")
        print("-" * 80)
        for row in rows:
            print(f"  ID: {row[0]}, teacher_id: {row[1]}, 姓名: {row[2]}, 身份证: {row[3]}")
        
        # 2. 检查 teacher_basic 表中的身份证列表
        cursor.execute('SELECT 身份证号码 FROM teacher_basic WHERE 身份证号码 IS NOT NULL')
        id_cards = set(row[0] for row in cursor.fetchall())
        
        print(f"\nteacher_basic 表中的身份证数量: {len(id_cards)}")
        
        # 3. 模拟导入过程
        # 假设用户上传的数据中有这些身份证
        # 实际上传的身份证可能不在 id_cards 中
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"错误: {e}")

if __name__ == "__main__":
    analyze()
