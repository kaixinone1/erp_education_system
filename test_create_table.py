#!/usr/bin/env python3
"""
测试创建表
"""

import psycopg2

DB_PARAMS = {
    'host': 'localhost',
    'database': 'taiping_education',
    'user': 'taiping_user',
    'password': 'taiping_password'
}

def test_create_table():
    conn = psycopg2.connect(**DB_PARAMS)
    cursor = conn.cursor()
    
    table_name = 'test_import_table'
    
    try:
        # 检查表是否存在
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = %s
            )
        """, (table_name,))
        
        exists = cursor.fetchone()[0]
        print(f"表 {table_name} 存在: {exists}")
        
        if exists:
            # 删除已存在的表
            cursor.execute(f"DROP TABLE {table_name}")
            conn.commit()
            print(f"✅ 已删除旧表 {table_name}")
        
        # 创建新表
        create_sql = f"""
            CREATE TABLE {table_name} (
                id SERIAL PRIMARY KEY,
                name VARCHAR(50),
                gender VARCHAR(10),
                birth_date DATE,
                age INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                import_batch VARCHAR(50)
            )
        """
        cursor.execute(create_sql)
        conn.commit()
        print(f"✅ 创建表 {table_name} 成功")
        
        # 插入测试数据
        cursor.execute(
            f"INSERT INTO {table_name} (name, gender, birth_date, age) VALUES (%s, %s, %s, %s)",
            ('张三', '男', '2001-01-01', 25)
        )
        conn.commit()
        print("✅ 插入数据成功")
        
        # 查询
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        print(f"查询结果: {rows}")
        
        # 清理
        cursor.execute(f"DROP TABLE {table_name}")
        conn.commit()
        print("✅ 测试表已删除")
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    test_create_table()
