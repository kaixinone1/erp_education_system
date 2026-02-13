#!/usr/bin/env python3
"""
检查并处理重复的教师学历记录表
"""

import psycopg2

# 数据库连接参数
DB_PARAMS = {
    'host': 'localhost',
    'database': 'taiping_education',
    'user': 'taiping_user',
    'password': 'taiping_password'
}

def check_tables():
    """检查教师相关的表"""
    print("检查教师学历相关的表...")
    
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cursor = conn.cursor()
        
        # 查询所有教师相关的表
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            AND table_name LIKE 'teacher%'
            ORDER BY table_name
        """)
        
        tables = cursor.fetchall()
        
        print(f"\n找到 {len(tables)} 个教师相关的表:")
        print("-" * 60)
        
        for (table_name,) in tables:
            # 查询每个表的记录数
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                
                # 查询表结构
                cursor.execute("""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = %s AND table_schema = 'public'
                    ORDER BY ordinal_position
                """, (table_name,))
                columns = cursor.fetchall()
                
                print(f"\n{table_name} ({count} 条数据)")
                print(f"  字段: {', '.join([col[0] for col in columns[:5]])}...")
            except Exception as e:
                print(f"\n{table_name} - 查询失败: {e}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"错误: {e}")

if __name__ == "__main__":
    check_tables()
