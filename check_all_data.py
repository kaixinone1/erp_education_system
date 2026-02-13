#!/usr/bin/env python3
"""
检查teacher_record表的所有数据
"""

import psycopg2

# 数据库连接参数
DB_PARAMS = {
    'host': 'localhost',
    'database': 'taiping_education',
    'user': 'taiping_user',
    'password': 'taiping_password'
}

def check_all_data():
    """检查teacher_record表的所有数据"""
    print("检查teacher_record表的所有数据...")
    
    try:
        # 连接数据库
        conn = psycopg2.connect(**DB_PARAMS)
        cursor = conn.cursor()
        
        # 查询表中的所有数据
        cursor.execute("SELECT id, 姓名, 身份证号码 FROM teacher_record ORDER BY id")
        rows = cursor.fetchall()
        
        print(f"表中共有 {len(rows)} 条数据:")
        print("-" * 80)
        print(f"{'ID':<5} {'姓名':<15} {'身份证号码':<20}")
        print("-" * 80)
        
        for row in rows:
            id, name, id_card = row
            print(f"{id:<5} {name:<15} {id_card:<20}")
        
        # 关闭连接
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"错误: {e}")

if __name__ == "__main__":
    check_all_data()
