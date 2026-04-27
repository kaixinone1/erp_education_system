#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
迁移 checklist_instances 数据到 todo_items 表
"""

import psycopg2
import json
from datetime import datetime

def get_db_connection():
    return psycopg2.connect(
        host='localhost',
        port='5432',
        database='taiping_education',
        user='taiping_user',
        password='taiping_password'
    )

def migrate():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        print("=== 开始迁移 checklist_instances 到 todo_items ===\n")
        
        # 查询 checklist_instances 数据
        cursor.execute("""
            SELECT id, 模板id, 关联对象id, 关联对象类型, 关联对象名称,
                   触发条件详情, 状态, 完成进度, 创建时间, 截止时间, 完成时间, 备注
            FROM checklist_instances
            ORDER BY 创建时间 DESC
        """)
        
        rows = cursor.fetchall()
        print(f"找到 {len(rows)} 条 checklist_instances 记录")
        
        migrated_count = 0
        
        for row in rows:
            (old_id, template_id, teacher_id, teacher_type, teacher_name,
             trigger_detail, status, progress, created_at, deadline, completed_at, remark) = row
            
            # 获取模板名称
            cursor.execute("SELECT 模板名称 FROM business_checklist_templates WHERE id = %s", (template_id,))
            template_result = cursor.fetchone()
            template_name = template_result[0] if template_result else '默认模板'
            
            # 查询或创建 todo_templates 中的模板
            cursor.execute("SELECT id FROM todo_templates WHERE template_name = %s", (template_name,))
            new_template_result = cursor.fetchone()
            
            if not new_template_result:
                # 创建模板
                cursor.execute("""
                    INSERT INTO todo_templates (template_code, template_name, business_type, description, due_date_rule, is_enabled, created_at)
                    VALUES (%s, %s, 'CUSTOM', %s, '7天', true, CURRENT_TIMESTAMP)
                    ON CONFLICT (template_code) DO NOTHING
                    RETURNING id
                """, (f"MIGRATE_{old_id}", template_name, f"从checklist_instances迁移的模板"))
                result = cursor.fetchone()
                new_template_id = result[0] if result else None
            else:
                new_template_id = new_template_result[0]
            
            # 映射状态
            status_map = {
                '待处理': 'pending',
                '进行中': 'in_progress',
                '已完成': 'completed',
                '已关闭': 'returned'
            }
            new_status = status_map.get(status, 'pending')
            
            # 计算任务数（从进度推算，假设总共10个任务）
            total_tasks = 10
            completed_tasks = int((progress or 0) / 100 * total_tasks)
            
            # 构建任务项列表
            task_items = []
            for i in range(total_tasks):
                task_status = 'completed' if i < completed_tasks else 'pending'
                task_items.append({
                    'name': f'任务{i+1}',
                    'status': task_status,
                    'completed_at': completed_at.isoformat() if completed_at and task_status == 'completed' else None
                })
            
            # 构建标题
            title = f"{teacher_name}的{template_name}（共{total_tasks}项，已完成{completed_tasks}项，{progress or 0}%）"
            
            # 插入 todo_items - 使用正确的字段名
            cursor.execute("""
                INSERT INTO todo_items (
                    template_id, business_type, teacher_id, teacher_name,
                    title, description, status, priority, due_date,
                    task_items, created_by, created_at, completed_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
                RETURNING id
            """, (
                str(new_template_id) if new_template_id else None,
                'CUSTOM',
                teacher_id,
                teacher_name,
                title,
                remark,
                new_status,
                'normal',
                deadline,
                json.dumps(task_items),
                'system',
                created_at or datetime.now(),
                completed_at
            ))
            
            result = cursor.fetchone()
            if result:
                migrated_count += 1
                print(f"  迁移: {title}")
        
        conn.commit()
        print(f"\n=== 迁移完成，共迁移 {migrated_count} 条记录 ===")
        
    except Exception as e:
        conn.rollback()
        print(f"[ERROR] 迁移失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    migrate()
