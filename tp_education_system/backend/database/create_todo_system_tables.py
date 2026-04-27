#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建新的统一待办系统数据库表
5个抽屉：
1. todo_items - 待办事项档案（核心）
2. todo_templates - 清单模板档案
3. trigger_conditions - 触发条件档案
4. pending_triggers - 待确认触发档案
5. user_custom_todos - 用户自定义待办档案
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

        # ========== 抽屉2：清单模板档案 ==========
        print("\n【抽屉2】创建清单模板表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS todo_templates (
                id SERIAL PRIMARY KEY,
                template_code VARCHAR(50) UNIQUE NOT NULL, -- 模板编号
                template_name VARCHAR(200) NOT NULL,       -- 模板名称
                business_type VARCHAR(50) NOT NULL,        -- 业务类型
                description TEXT,                          -- 模板说明
                task_flow JSONB,                           -- 任务流程（JSON格式，可拖拽设计）
                due_date_rule VARCHAR(100),                -- 截止日期规则
                default_priority VARCHAR(20) DEFAULT 'normal', -- 默认优先级
                is_enabled BOOLEAN DEFAULT TRUE,           -- 是否启用
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("  [OK] 清单模板表创建成功")

        # 插入默认模板
        print("\n  插入默认清单模板...")
        
        # 退休模板
        cursor.execute("""
            INSERT INTO todo_templates (template_code, template_name, business_type, description, task_flow, due_date_rule)
            VALUES (
                'RETIREMENT_001',
                '退休教师呈报业务清单',
                'RETIREMENT',
                '教师退休需要办理的各项业务手续',
                '[
                    {"step": 1, "title": "收集退休申请材料", "type": "收集", "required": true, "days": 3},
                    {"step": 2, "title": "填写退休审批表", "type": "填写", "required": true, "days": 2},
                    {"step": 3, "title": "单位领导签字", "type": "审批", "required": true, "days": 2},
                    {"step": 4, "title": "教育局审批", "type": "审批", "required": true, "days": 5},
                    {"step": 5, "title": "人社局审批", "type": "审批", "required": true, "days": 10}
                ]'::jsonb,
                '触发后+30天'
            )
            ON CONFLICT (template_code) DO NOTHING
        """)
        
        # 去世模板
        cursor.execute("""
            INSERT INTO todo_templates (template_code, template_name, business_type, description, task_flow, due_date_rule)
            VALUES (
                'DEATH_001',
                '教师死亡后待办工作',
                'DEATH',
                '教师去世后需要办理的各项业务手续',
                '[
                    {"step": 1, "title": "收集死亡证明", "type": "收集", "required": true, "days": 1},
                    {"step": 2, "title": "打印终保承诺书", "type": "打印", "required": true, "days": 1},
                    {"step": 3, "title": "扫描上传材料", "type": "上传", "required": true, "days": 2},
                    {"step": 4, "title": "填报抚恤金审批表", "type": "填写", "required": true, "days": 3},
                    {"step": 5, "title": "送审材料", "type": "送审", "required": true, "days": 2},
                    {"step": 6, "title": "机关中心签批", "type": "审批", "required": true, "days": 3},
                    {"step": 7, "title": "工资科预审核", "type": "审批", "required": true, "days": 3},
                    {"step": 8, "title": "教育局审批", "type": "审批", "required": true, "days": 5},
                    {"step": 9, "title": "人社局审批", "type": "审批", "required": true, "days": 5},
                    {"step": 10, "title": "财政局备案", "type": "备案", "required": true, "days": 2}
                ]'::jsonb,
                '触发后+7天'
            )
            ON CONFLICT (template_code) DO NOTHING
        """)
        
        # 80周岁模板
        cursor.execute("""
            INSERT INTO todo_templates (template_code, template_name, business_type, description, task_flow, due_date_rule)
            VALUES (
                'OCTOGENARIAN_001',
                '80周岁高龄补贴业务清单',
                'OCTOGENARIAN',
                '教师满80周岁需要办理的高龄补贴业务',
                '[
                    {"step": 1, "title": "收集身份证、户口本复印件", "type": "收集", "required": true, "days": 5},
                    {"step": 2, "title": "填写高龄补贴申请表", "type": "填写", "required": true, "days": 3},
                    {"step": 3, "title": "单位审核盖章", "type": "审批", "required": true, "days": 3},
                    {"step": 4, "title": "提交民政部门", "type": "送审", "required": true, "days": 5}
                ]'::jsonb,
                '80周岁生日当天'
            )
            ON CONFLICT (template_code) DO NOTHING
        """)
        
        # 到龄退休提醒模板
        cursor.execute("""
            INSERT INTO todo_templates (template_code, template_name, business_type, description, task_flow, due_date_rule)
            VALUES (
                'RETIREMENT_REMIND',
                '到龄退休提醒清单',
                'RETIREMENT_REMIND',
                '教师即将到龄退休的提醒',
                '[
                    {"step": 1, "title": "核实教师档案信息", "type": "核实", "required": true, "days": 3},
                    {"step": 2, "title": "通知教师准备材料", "type": "通知", "required": true, "days": 7},
                    {"step": 3, "title": "确认退休时间", "type": "确认", "required": true, "days": 7}
                ]'::jsonb,
                '退休日期'
            )
            ON CONFLICT (template_code) DO NOTHING
        """)
        print("  [OK] 默认模板插入成功")

        # ========== 抽屉3：触发条件档案 ==========
        print("\n【抽屉3】创建触发条件表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trigger_conditions (
                id SERIAL PRIMARY KEY,
                condition_name VARCHAR(200) NOT NULL,    -- 条件名称
                listen_table VARCHAR(100) NOT NULL,      -- 监听哪个表
                listen_field VARCHAR(100) NOT NULL,      -- 监听哪个字段
                trigger_type VARCHAR(50) NOT NULL,       -- 触发方式：change/equal/contain/date/numeric
                trigger_value VARCHAR(200),              -- 触发值（如果是equal/contain）
                advance_notice VARCHAR(50),              -- 提前通知时间（如：7周、2个月）
                template_code VARCHAR(50) NOT NULL,      -- 关联的模板编号
                is_enabled BOOLEAN DEFAULT TRUE,         -- 是否启用
                description TEXT,                        -- 条件说明
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("  [OK] 触发条件表创建成功")

        # 插入默认触发条件
        print("\n  插入默认触发条件...")
        
        # 退休触发
        cursor.execute("""
            INSERT INTO trigger_conditions (condition_name, listen_table, listen_field, trigger_type, trigger_value, template_code, description)
            VALUES (
                '任职状态变为退休',
                'teacher_basic_info',
                'employment_status',
                'equal',
                '退休',
                'RETIREMENT_001',
                '当教师任职状态变为退休时，推送退休业务清单'
            )
            ON CONFLICT DO NOTHING
        """)
        
        # 去世触发
        cursor.execute("""
            INSERT INTO trigger_conditions (condition_name, listen_table, listen_field, trigger_type, trigger_value, template_code, description)
            VALUES (
                '任职状态变为去世',
                'teacher_basic_info',
                'employment_status',
                'equal',
                '去世',
                'DEATH_001',
                '当教师任职状态变为去世时，推送死亡待办清单'
            )
            ON CONFLICT DO NOTHING
        """)
        print("  [OK] 默认触发条件插入成功")

        # ========== 抽屉4：待确认触发档案 ==========
        print("\n【抽屉4】创建待确认触发表...")
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

        # ========== 抽屉5：用户自定义待办档案 ==========
        print("\n【抽屉5】创建用户自定义待办表...")
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
