#!/usr/bin/env python3
"""
将 data_452489 表重命名为 teacher_basic
"""

import psycopg2

# 数据库连接参数
DB_PARAMS = {
    'host': 'localhost',
    'database': 'taiping_education',
    'user': 'taiping_user',
    'password': 'taiping_password'
}

def rename_table():
    """重命名表"""
    print("准备将 data_452489 重命名为 teacher_basic...")
    
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cursor = conn.cursor()
        
        # 检查 data_452489 表是否存在
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'data_452489'
            )
        """)
        exists = cursor.fetchone()[0]
        
        if not exists:
            print("表 data_452489 不存在，无需重命名")
            cursor.close()
            conn.close()
            return
        
        # 检查 teacher_basic 表是否已存在
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'teacher_basic'
            )
        """)
        teacher_basic_exists = cursor.fetchone()[0]
        
        if teacher_basic_exists:
            print("表 teacher_basic 已存在，先删除它")
            cursor.execute("DROP TABLE IF EXISTS teacher_basic CASCADE")
            conn.commit()
        
        # 重命名表
        cursor.execute("ALTER TABLE data_452489 RENAME TO teacher_basic")
        conn.commit()
        
        print("✓ 表重命名成功: data_452489 -> teacher_basic")
        
        # 查询重命名后的表数据量
        cursor.execute("SELECT COUNT(*) FROM teacher_basic")
        count = cursor.fetchone()[0]
        print(f"  表中共有 {count} 条数据")
        
        # 查询表结构
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'teacher_basic'
            ORDER BY ordinal_position
        """)
        columns = cursor.fetchall()
        print(f"  表结构 ({len(columns)} 个字段):")
        for col_name, data_type in columns[:5]:  # 只显示前5个字段
            print(f"    - {col_name}: {data_type}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"错误: {e}")

if __name__ == "__main__":
    rename_table()
