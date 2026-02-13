#!/usr/bin/env python3
"""
简单测试插入
"""

import psycopg2

DB_PARAMS = {
    'host': 'localhost',
    'database': 'taiping_education',
    'user': 'taiping_user',
    'password': 'taiping_password'
}

def test_insert():
    conn = psycopg2.connect(**DB_PARAMS)
    cursor = conn.cursor()
    
    try:
        # 创建测试表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_simple (
                id SERIAL PRIMARY KEY,
                name VARCHAR(50),
                age INTEGER
            )
        """)
        
        # 插入数据
        cursor.execute(
            "INSERT INTO test_simple (name, age) VALUES (%s, %s)",
            ('张三', 25)
        )
        
        conn.commit()
        print("✅ 插入成功")
        
        # 查询数据
        cursor.execute("SELECT * FROM test_simple")
        rows = cursor.fetchall()
        print(f"查询结果: {rows}")
        
        # 删除测试表
        cursor.execute("DROP TABLE test_simple")
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
    test_insert()
