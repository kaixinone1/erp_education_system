#!/usr/bin/env python3
"""
创建手动待办功能所需的数据库表
"""

import psycopg2
from psycopg2.extras import RealDictCursor

def get_db_connection():
    return psycopg2.connect(
        host='localhost',
        port='5432',
        database='taiping_education',
        user='taiping_user',
        password='taiping_password'
    )

def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 1. 在 todo_work 表中添加新字段
        print("[1/2] 修改 todo_work 表...")
        
        # 检查字段是否存在
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'todo_work' AND column_name = 'is_manual'
        """)
        
        if not cursor.fetchone():
            cursor.execute("""
                ALTER TABLE todo_work 
                ADD COLUMN is_manual BOOLEAN DEFAULT FALSE,
                ADD COLUMN priority VARCHAR(10) DEFAULT 'normal',
                ADD COLUMN description TEXT,
                ADD COLUMN completed_at TIMESTAMP
            """)
            print("  ✓ 添加字段: is_manual, priority, description, completed_at")
        else:
            print("  ℹ 字段已存在，跳过")
        
        # 2. 创建子任务表
        print("[2/2] 创建 todo_items 子任务表...")
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS todo_items (
                id SERIAL PRIMARY KEY,
                todo_id INTEGER NOT NULL REFERENCES todo_work(id) ON DELETE CASCADE,
                item_name VARCHAR(200) NOT NULL,
                is_completed BOOLEAN DEFAULT FALSE,
                completed_at TIMESTAMP,
                sort_order INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("  ✓ 创建表 todo_items")
        
        # 创建索引
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_todo_items_todo_id 
            ON todo_items(todo_id)
        """)
        print("  ✓ 创建索引 idx_todo_items_todo_id")
        
        conn.commit()
        print("\n========================================")
        print("  数据库表创建成功！")
        print("========================================")
        
    except Exception as e:
        conn.rollback()
        print(f"\n✗ 错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    create_tables()
