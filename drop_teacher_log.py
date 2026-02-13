#!/usr/bin/env python3
"""
删除 teacher_log 表
"""

import psycopg2

# 数据库连接参数
DB_PARAMS = {
    'host': 'localhost',
    'database': 'taiping_education',
    'user': 'taiping_user',
    'password': 'taiping_password'
}

def drop_teacher_log():
    """删除 teacher_log 表"""
    print("准备删除 teacher_log 表...")
    
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cursor = conn.cursor()
        
        # 先查询表的数据量
        cursor.execute("SELECT COUNT(*) FROM teacher_log")
        count = cursor.fetchone()[0]
        print(f"teacher_log 表中有 {count} 条数据")
        
        # 确认删除
        print("\n正在删除 teacher_log 表...")
        cursor.execute("DROP TABLE IF EXISTS teacher_log CASCADE")
        conn.commit()
        
        print("✅ teacher_log 表已成功删除！")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ 删除失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    drop_teacher_log()
