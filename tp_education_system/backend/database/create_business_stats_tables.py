
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
为每类业务创建独立的统计表
"""

import psycopg2
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def create_stats_tables():
    """为每类业务创建独立的统计表"""
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
        print("开始为每类业务创建独立的统计表")
        print("=" * 60)

        # ========== 1. 到龄退休提醒统计表 ==========
        print("\n【统计表1】创建到龄退休提醒统计表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS retirement_reminder_stats (
                id SERIAL PRIMARY KEY,
                todo_item_id INTEGER NOT NULL,           -- 关联的待办事项ID
                teacher_id INTEGER,                      -- 教师ID
                teacher_name VARCHAR(100),               -- 教师姓名
                create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- 产生时间
                start_process_time TIMESTAMP,             -- 开始处理时间
                progress_update_time TIMESTAMP,           -- 进度更新时间
                complete_time TIMESTAMP,                  -- 完成时间
                return_time TIMESTAMP,                    -- 退回时间
                current_progress INTEGER DEFAULT 0,       -- 当前进度(%)
                total_tasks INTEGER DEFAULT 0,            -- 总任务数
                completed_tasks INTEGER DEFAULT 0,        -- 已完成任务数
                status VARCHAR(20) DEFAULT 'pending',     -- 当前状态
                notes TEXT,                                -- 备注
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("  [OK] 到龄退休提醒统计表创建成功")

        # ========== 2. 到龄退休审批统计表 ==========
        print("\n【统计表2】创建到龄退休审批统计表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS retirement_approval_stats (
                id SERIAL PRIMARY KEY,
                todo_item_id INTEGER NOT NULL,
                teacher_id INTEGER,
                teacher_name VARCHAR(100),
                create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                start_process_time TIMESTAMP,
                progress_update_time TIMESTAMP,
                complete_time TIMESTAMP,
                return_time TIMESTAMP,
                current_progress INTEGER DEFAULT 0,
                total_tasks INTEGER DEFAULT 0,
                completed_tasks INTEGER DEFAULT 0,
                status VARCHAR(20) DEFAULT 'pending',
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("  [OK] 到龄退休审批统计表创建成功")

        # ========== 3. 死亡登记统计表 ==========
        print("\n【统计表3】创建死亡登记统计表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS death_registration_stats (
                id SERIAL PRIMARY KEY,
                todo_item_id INTEGER NOT NULL,
                teacher_id INTEGER,
                teacher_name VARCHAR(100),
                create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                start_process_time TIMESTAMP,
                progress_update_time TIMESTAMP,
                complete_time TIMESTAMP,
                return_time TIMESTAMP,
                current_progress INTEGER DEFAULT 0,
                total_tasks INTEGER DEFAULT 0,
                completed_tasks INTEGER DEFAULT 0,
                status VARCHAR(20) DEFAULT 'pending',
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("  [OK] 死亡登记统计表创建成功")

        # ========== 4. 80周岁高龄补贴申请表 ==========
        print("\n【统计表4】创建80周岁高龄补贴统计表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS octogenarian_subsidy_stats (
                id SERIAL PRIMARY KEY,
                todo_item_id INTEGER NOT NULL,
                teacher_id INTEGER,
                teacher_name VARCHAR(100),
                create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                start_process_time TIMESTAMP,
                progress_update_time TIMESTAMP,
                complete_time TIMESTAMP,
                return_time TIMESTAMP,
                current_progress INTEGER DEFAULT 0,
                total_tasks INTEGER DEFAULT 0,
                completed_tasks INTEGER DEFAULT 0,
                status VARCHAR(20) DEFAULT 'pending',
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("  [OK] 80周岁高龄补贴统计表创建成功")

        # ========== 5. 自定义待办统计表 ==========
        print("\n【统计表5】创建自定义待办统计表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS custom_todo_stats (
                id SERIAL PRIMARY KEY,
                todo_item_id INTEGER NOT NULL,
                teacher_id INTEGER,
                teacher_name VARCHAR(100),
                create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                start_process_time TIMESTAMP,
                progress_update_time TIMESTAMP,
                complete_time TIMESTAMP,
                return_time TIMESTAMP,
                current_progress INTEGER DEFAULT 0,
                total_tasks INTEGER DEFAULT 0,
                completed_tasks INTEGER DEFAULT 0,
                status VARCHAR(20) DEFAULT 'pending',
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("  [OK] 自定义待办统计表创建成功")

        # ========== 创建索引 ==========
        print("\n创建索引...")
        
        tables = [
            'retirement_reminder_stats',
            'retirement_approval_stats', 
            'death_registration_stats',
            'octogenarian_subsidy_stats',
            'custom_todo_stats'
        ]
        
        for table in tables:
            cursor.execute(f"""
                CREATE INDEX IF NOT EXISTS idx_{table}_todo_item_id 
                ON {table}(todo_item_id)
            """)
            cursor.execute(f"""
                CREATE INDEX IF NOT EXISTS idx_{table}_teacher_id 
                ON {table}(teacher_id)
            """)
            cursor.execute(f"""
                CREATE INDEX IF NOT EXISTS idx_{table}_status 
                ON {table}(status)
            """)
            cursor.execute(f"""
                CREATE INDEX IF NOT EXISTS idx_{table}_create_time 
                ON {table}(create_time)
            """)
        print("  [OK] 所有索引创建成功")

        # ========== 将现有数据迁移到统计表 ==========
        print("\n将现有待办数据迁移到对应的统计表...")
        
        # 先查询所有待办数据 - 使用正确的字段名
        cursor.execute("""
            SELECT id, business_type, teacher_id, teacher_name,
                   created_at, completed_at,
                   status, task_items
            FROM todo_items
        """)
        todo_items = cursor.fetchall()
        
        for todo in todo_items:
            todo_id, business_type, teacher_id, teacher_name, created_at, completed_at, status, task_items = todo
            
            # 计算任务统计
            if task_items:
                if isinstance(task_items, str):
                    import json
                    task_items = json.loads(task_items)
                total_tasks = len(task_items)
                completed_tasks = sum(1 for t in task_items if t.get('status') == 'completed' or t.get('completed') == True)
                progress = int(completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            else:
                total_tasks = 0
                completed_tasks = 0
                progress = 0
            
            # 根据业务类型选择对应的统计表
            table_name = None
            business_type_lower = business_type.lower() if business_type else ''
            
            if business_type_lower == 'retirement_reminder':
                table_name = 'retirement_reminder_stats'
            elif business_type_lower == 'retirement_approval':
                table_name = 'retirement_approval_stats'
            elif business_type_lower == 'death_registration':
                table_name = 'death_registration_stats'
            elif business_type_lower == 'octogenarian_subsidy':
                table_name = 'octogenarian_subsidy_stats'
            elif business_type_lower == 'custom':
                table_name = 'custom_todo_stats'
            else:
                # 默认归入自定义待办
                table_name = 'custom_todo_stats'
            
            if table_name:
                # 检查是否已存在记录
                cursor.execute(f"""
                    SELECT id FROM {table_name} WHERE todo_item_id = %s
                """, (todo_id,))
                if not cursor.fetchone():
                    # 插入新记录
                    cursor.execute(f"""
                        INSERT INTO {table_name} (
                            todo_item_id, teacher_id, teacher_name,
                            create_time, complete_time,
                            current_progress, total_tasks, completed_tasks, status
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        todo_id, teacher_id, teacher_name,
                        created_at, completed_at,
                        progress, total_tasks, completed_tasks, status
                    ))
                    print(f"  已迁移待办 {todo_id} ({teacher_name}) 到 {table_name}")
        
        conn.commit()
        print("\n" + "=" * 60)
        print("所有业务统计表创建完成！")
        print("=" * 60)

    except Exception as e:
        conn.rollback()
        print(f"\n[ERROR] 创建表失败: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    create_stats_tables()
