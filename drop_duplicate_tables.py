#!/usr/bin/env python3
"""
删除重复的教师学历记录表，只保留 teacher_record 作为标准表名
"""

import psycopg2

# 数据库连接参数
DB_PARAMS = {
    'host': 'localhost',
    'database': 'taiping_education',
    'user': 'taiping_user',
    'password': 'taiping_password'
}

def drop_duplicate_tables():
    """删除重复的表"""
    print("准备删除重复的教师学历记录表...")
    
    # 要删除的表（保留 teacher_basic 主表）
    tables_to_drop = ['teacher_archive', 'teacher_history', 'teacher_log']
    
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cursor = conn.cursor()
        
        for table_name in tables_to_drop:
            try:
                # 检查表是否存在
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = %s AND table_schema = 'public'
                    )
                """, (table_name,))
                exists = cursor.fetchone()[0]
                
                if exists:
                    # 查询表中的数据量
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    count = cursor.fetchone()[0]
                    
                    if count == 0:
                        # 表为空，可以安全删除
                        cursor.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE")
                        conn.commit()
                        print(f"✓ 已删除空表: {table_name}")
                    else:
                        print(f"⚠️ 表 {table_name} 有 {count} 条数据，不删除")
                else:
                    print(f"  表 {table_name} 不存在，跳过")
                    
            except Exception as e:
                print(f"✗ 删除表 {table_name} 失败: {e}")
                conn.rollback()
        
        cursor.close()
        conn.close()
        
        print("\n清理完成！")
        
    except Exception as e:
        print(f"错误: {e}")

if __name__ == "__main__":
    drop_duplicate_tables()
