#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
给todo_items表添加notes字段
"""

import psycopg2

def add_notes_column():
    conn = psycopg2.connect(
        host='localhost', port='5432', database='taiping_education',
        user='taiping_user', password='taiping_password'
    )
    cursor = conn.cursor()

    try:
        print("=" * 60)
        print("给todo_items表添加notes字段")
        print("=" * 60)

        # 检查字段是否已存在
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'todo_items' AND column_name = 'notes'
        """)
        
        if cursor.fetchone():
            print("  [OK] notes字段已存在")
        else:
            # 添加notes字段
            cursor.execute("""
                ALTER TABLE todo_items 
                ADD COLUMN notes JSONB DEFAULT '[]'::jsonb
            """)
            print("  [OK] notes字段添加成功")
        
        conn.commit()
        print("\n" + "=" * 60)
        print("完成！")
        print("=" * 60)

    except Exception as e:
        conn.rollback()
        print(f"\n[ERROR] 添加字段失败: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    add_notes_column()
