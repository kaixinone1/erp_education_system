
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
给todo_items表添加必要的字段
"""

import psycopg2
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def add_fields():
    conn = psycopg2.connect(
        host='localhost',
        port='5432',
        database='taiping_education',
        user='taiping_user',
        password='taiping_password'
    )
    cursor = conn.cursor()

    try:
        print("=" * 60)
        print("给todo_items表添加必要的字段")
        print("=" * 60)

        # 添加 started_at 字段
        print("\n添加 started_at 字段...")
        cursor.execute("""
            ALTER TABLE todo_items 
            ADD COLUMN IF NOT EXISTS started_at TIMESTAMP
        """)
        print("  [OK] started_at 字段添加成功")

        # 添加 returned_at 字段
        print("\n添加 returned_at 字段...")
        cursor.execute("""
            ALTER TABLE todo_items 
            ADD COLUMN IF NOT EXISTS returned_at TIMESTAMP
        """)
        print("  [OK] returned_at 字段添加成功")

        conn.commit()
        print("\n" + "=" * 60)
        print("字段添加完成！")
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
    add_fields()
