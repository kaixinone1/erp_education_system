"""
数据库迁移脚本：统一待办工作状态为中文
1. 添加 completed_at 和 sort_order 字段
2. 将现有状态从英文改为中文
"""
import psycopg2

def migrate_database():
    conn = psycopg2.connect(
        host='localhost',
        port=5432,
        database='taiping_education',
        user='taiping_user',
        password='taiping_password'
    )
    cursor = conn.cursor()
    
    try:
        print("=" * 60)
        print("开始数据库迁移：统一待办工作状态为中文")
        print("=" * 60)
        
        # 1. 添加 completed_at 字段（如果不存在）
        print("\n步骤1: 检查并添加 completed_at 字段...")
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='todo_work' AND column_name='completed_at'
        """)
        if not cursor.fetchone():
            cursor.execute("""
                ALTER TABLE todo_work 
                ADD COLUMN completed_at TIMESTAMP
            """)
            print("  [OK] completed_at 字段已添加")
        else:
            print("  [INFO] completed_at 字段已存在")
        
        # 2. 添加 sort_order 字段（如果不存在）
        print("\n步骤2: 检查并添加 sort_order 字段...")
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='todo_work' AND column_name='sort_order'
        """)
        if not cursor.fetchone():
            cursor.execute("""
                ALTER TABLE todo_work 
                ADD COLUMN sort_order INTEGER DEFAULT 0
            """)
            print("  [OK] sort_order 字段已添加")
        else:
            print("  [INFO] sort_order 字段已存在")
        
        # 3. 更新现有状态：将英文状态改为中文
        print("\n步骤3: 更新现有状态为中文...")
        
        # 统计需要更新的记录数
        cursor.execute("""
            SELECT COUNT(*) FROM todo_work 
            WHERE 状态 IN ('pending', 'in_progress', 'completed')
        """)
        count = cursor.fetchone()[0]
        print(f"  [INFO] 发现 {count} 条需要更新的记录")
        
        if count > 0:
            # 更新状态
            cursor.execute("""
                UPDATE todo_work 
                SET 状态 = CASE 
                    WHEN 状态 = 'pending' THEN '待处理'
                    WHEN 状态 = 'in_progress' THEN '进行中'
                    WHEN 状态 = 'completed' THEN '已完成'
                    ELSE 状态
                END
                WHERE 状态 IN ('pending', 'in_progress', 'completed')
            """)
            print(f"  [OK] 已更新 {cursor.rowcount} 条记录的状态")
        
        # 4. 设置已完成记录的 completed_at 时间
        print("\n步骤4: 设置已完成记录的 completed_at 时间...")
        cursor.execute("""
            UPDATE todo_work 
            SET completed_at = updated_at,
                sort_order = 999
            WHERE 状态 = '已完成' AND completed_at IS NULL
        """)
        print(f"  [OK] 已设置 {cursor.rowcount} 条已完成记录的 completed_at 时间")
        
        # 5. 设置未完成记录的 sort_order
        print("\n步骤5: 设置未完成记录的 sort_order...")
        cursor.execute("""
            UPDATE todo_work 
            SET sort_order = 0
            WHERE 状态 IN ('待处理', '进行中') AND sort_order = 0
        """)
        print(f"  [OK] 已设置 {cursor.rowcount} 条未完成记录的 sort_order")
        
        # 提交事务
        conn.commit()
        
        print("\n" + "=" * 60)
        print("数据库迁移完成！")
        print("=" * 60)
        
        # 验证结果
        print("\n验证结果：")
        cursor.execute("""
            SELECT 状态, COUNT(*) 
            FROM todo_work 
            GROUP BY 状态
        """)
        results = cursor.fetchall()
        for status, count in results:
            print(f"  {status}: {count} 条")
        
    except Exception as e:
        conn.rollback()
        print(f"\n[ERROR] 迁移失败: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    migrate_database()
