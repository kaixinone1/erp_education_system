#!/usr/bin/env python3
"""
升级 navigation_modules 表结构
添加 table_name, api_endpoint, component 字段
"""
import psycopg2

DATABASE_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'taiping_education',
    'user': 'taiping_user',
    'password': 'taiping_password'
}


def migrate():
    conn = psycopg2.connect(**DATABASE_CONFIG)
    cursor = conn.cursor()
    
    print("开始升级 navigation_modules 表...")
    
    # 添加新字段
    new_columns = [
        ('table_name', 'VARCHAR(100)'),
        ('api_endpoint', 'VARCHAR(200)'),
        ('component', 'VARCHAR(100)')
    ]
    
    for col_name, col_type in new_columns:
        try:
            cursor.execute(f"""
                ALTER TABLE navigation_modules 
                ADD COLUMN IF NOT EXISTS {col_name} {col_type}
            """)
            print(f"[OK] 添加字段: {col_name}")
        except Exception as e:
            print(f"[ERROR] 添加字段 {col_name} 失败: {e}")
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print("\n表结构升级完成！")


if __name__ == "__main__":
    migrate()
