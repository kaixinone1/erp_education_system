#!/usr/bin/env python3
"""
检查父表映射
"""

import psycopg2

DB_PARAMS = {
    'host': 'localhost',
    'database': 'taiping_education',
    'user': 'taiping_user',
    'password': 'taiping_password'
}

def check_parent_map():
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cursor = conn.cursor()
        
        # 查询 teacher_basic 表的字段
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'teacher_basic' AND table_schema = 'public'
            ORDER BY ordinal_position
        """)
        columns = [row[0] for row in cursor.fetchall()]
        print(f"teacher_basic 表字段: {columns}")
        
        # 查找身份证号码字段
        id_card_column = None
        for col in columns:
            if '身份证' in col:
                id_card_column = col
                break
        
        print(f"身份证号码字段: {id_card_column}")
        
        if id_card_column:
            # 查询前5条数据的id和身份证号码
            cursor.execute(f'SELECT id, "{id_card_column}" FROM teacher_basic LIMIT 5')
            rows = cursor.fetchall()
            print(f"\n前5条数据:")
            for row in rows:
                print(f"  ID: {row[0]}, 身份证: {row[1]}")
        
        # 查询特定身份证号码
        cursor.execute('SELECT id FROM teacher_basic WHERE "身份证号码" = %s', ('110101199001011234',))
        result = cursor.fetchone()
        print(f"\n查询 110101199001011234: {result}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_parent_map()
