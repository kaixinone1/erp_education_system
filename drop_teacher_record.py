#!/usr/bin/env python3
"""
删除teacher_record表
"""

import psycopg2

# 数据库连接参数
DB_PARAMS = {
    'host': 'localhost',
    'database': 'taiping_education',
    'user': 'taiping_user',
    'password': 'taiping_password'
}

def drop_table():
    """删除teacher_record表"""
    print("准备删除teacher_record表...")
    
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cursor = conn.cursor()
        
        # 先查询表中的数据量
        cursor.execute("SELECT COUNT(*) FROM teacher_record")
        count = cursor.fetchone()[0]
        print(f"表中现有 {count} 条数据")
        
        # 删除表
        cursor.execute("DROP TABLE IF EXISTS teacher_record CASCADE")
        conn.commit()
        
        print("✓ teacher_record表已成功删除")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"错误: {e}")

if __name__ == "__main__":
    drop_table()
