#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建新的统一待办系统数据库表
5个抽屉：
1. todo_items - 待办事项档案（核心）
2. pending_triggers - 待确认触发档案
3. user_custom_todos - 用户自定义待办档案
"""

import psycopg2
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def create_tables():
    """创建统一待办系统所有表"""
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
        print("开始创建统一待办系统数据库表")
        print("=" * 60)

        # ========== 抽屉1：待办事项档案 ==========
        print("\n【抽屉1】创建待办事项表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS todo_items (
                id SERIAL PRIMARY KEY,
                template_id VARCHAR(50),           -- 关联的模板编号
                business_type VARCHAR(50) NOT NULL, -- 业务类型：RETIREMENT/DEATH/OCTOGENARIAN/CUSTOM
                teacher_id INTEGER,                 -- 教师ID
                teacher_name VARCHAR(100),          -- 教师姓名
                title VARCHAR(200) NOT NULL,        -- 待办标题
                description TEXT,                   -- 待办描述
                status VARCHAR(20) DEFAULT 'pending', -- 状态：pending/completed/returned
                priority VARCHAR(20) DEFAULT 'normal', -- 优先级：high/normal/low
                due_date DATE,                      -- 截止日期
                task_items JSONB,                   -- 任务项列表（JSON格式）
                created_by VARCHAR(20) DEFAULT 'system', -- 创建来源：system/user/auto
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- 创建时间
                completed_at TIMESTAMP,             -- 完成时间
                return_reason TEXT,                 -- 退回原因
                trigger_id INTEGER,                 -- 关联的触发记录ID
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- 更新时间
            )
        """)
        print("  [OK] 待办事项表创建成功")

        # 创建索引
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_todo_items_status 
            ON todo_items(status)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_todo_items_business_type 
            ON todo_items(business_type)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_todo_items_teacher_id 
            ON todo_items(teacher_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_todo_items_due_date 
            ON todo_items(due_date)
        """)
        print("  [OK] 待办事项表索引创建成功")

        # ========== 抽屉2：待确认触发档案 ==========
        print("\n【抽屉2】创建待确认触发表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pending_triggers (
                id SERIAL PRIMARY KEY,
                trigger_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- 触发时间
                trigger_reason TEXT NOT NULL,      -- 触发原因说明
                listen_table VARCHAR(100),         -- 监听的表
                listen_field VARCHAR(100),         -- 监听的字段
                old_value TEXT,                    -- 原值
                new_value TEXT,                    -- 新值
                teacher_id INTEGER,                -- 教师ID
                teacher_name VARCHAR(100),         -- 教师姓名
                template_code VARCHAR(50),         -- 关联模板编号
                template_name VARCHAR(200),        -- 模板名称
                status VARCHAR(20) DEFAULT 'pending', -- 状态：pending/confirmed/rejected
                handler VARCHAR(100),              -- 处理人
                handle_time TIMESTAMP,             -- 处理时间
                handle_note TEXT,                  -- 处理备注
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("  [OK] 待确认触发表创建成功")

        # 创建索引
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_pending_triggers_status 
            ON pending_triggers(status)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_pending_triggers_teacher_id 
            ON pending_triggers(teacher_id)
        """)
        print("  [OK] 待确认触发表索引创建成功")

        # ========== 抽屉3：用户自定义待办档案 ==========
        print("\n【抽屉3】创建用户自定义待办表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_custom_todos (
                id SERIAL PRIMARY KEY,
                creator VARCHAR(100) NOT NULL,     -- 创建人
                title VARCHAR(200) NOT NULL,       -- 待办标题
                description TEXT,                  -- 详细说明
                plan_date DATE,                    -- 计划办理日期
                remind_days INTEGER DEFAULT 7,     -- 提前几天提醒
                related_teacher_id INTEGER,        -- 关联教师ID（可选）
                related_teacher_name VARCHAR(100), -- 关联教师姓名（可选）
                status VARCHAR(20) DEFAULT 'pending', -- 状态
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("  [OK] 用户自定义待办表创建成功")

        # 创建索引
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_custom_todos_status 
            ON user_custom_todos(status)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_custom_todos_creator 
            ON user_custom_todos(creator)
        """)
        print("  [OK] 用户自定义待办表索引创建成功")

        conn.commit()
        print("\n" + "=" * 60)
        print("所有表创建成功！")
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
    create_tables()
