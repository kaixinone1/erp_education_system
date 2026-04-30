#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整的待办业务数据迁移脚本
迁移所有旧系统数据到新系统
"""

import psycopg2
from datetime import datetime
import json

def get_db_connection():
    """获取数据库连接"""
    return psycopg2.connect(
        host='localhost',
        port='5432',
        database='taiping_education',
        user='taiping_user',
        password='taiping_password'
    )

def migrate_from_checklist_instances():
    """从 business_checklist_instances 迁移数据"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        print("[OK] 开始从 business_checklist_instances 迁移数据...")
        
        # 查询旧表数据
        cursor.execute("""
            SELECT id, 模板ID, 关联对象ID, 关联对象名称, 关联对象编码,
                   状态, 创建时间, 截止时间, 实际完成时间, 处理人, 备注,
                   总任务数, 已完成数, 完成进度
            FROM business_checklist_instances
            ORDER BY 创建时间 DESC
        """)
        
        rows = cursor.fetchall()
        migrated_count = 0
        
        for row in rows:
            (old_id, template_id, teacher_id, teacher_name, teacher_code,
             status, created_at, deadline, completed_at, operator, remark,
             total_tasks, completed_tasks, progress) = row
            
            # 映射状态
            status_map = {
                '待处理': 'pending',
                '进行中': 'in_progress',
                '已完成': 'completed',
                '已关闭': 'returned',
                '已逾期': 'pending'
            }
            new_status = status_map.get(status, 'pending')
            
            # 获取模板名称
            cursor.execute("SELECT 模板名称 FROM business_checklist_templates WHERE id = %s", (template_id,))
            template_result = cursor.fetchone()
            template_name = template_result[0] if template_result else '默认模板'
            
            # 查询新表中的模板ID
            cursor.execute("SELECT id FROM todo_templates WHERE template_name = %s", (template_name,))
            new_template_result = cursor.fetchone()
            new_template_id = new_template_result[0] if new_template_result else None
            
            # 如果没有找到模板，创建一个默认模板
            if not new_template_id:
                cursor.execute("""
                    INSERT INTO todo_templates (template_code, template_name, business_type, description, due_date_rule, is_enabled, created_at)
                    VALUES (%s, %s, 'CUSTOM', '自动迁移的模板', '7天', true, CURRENT_TIMESTAMP)
                    ON CONFLICT (template_code) DO NOTHING
                    RETURNING id
                """, (f"AUTO_{old_id}", template_name))
                result = cursor.fetchone()
                if result:
                    new_template_id = result[0]
            
            # 构建任务流程
            task_flow = []
            if total_tasks and total_tasks > 0:
                for i in range(total_tasks):
                    task_status = 'completed' if completed_tasks and i < completed_tasks else 'pending'
                    task_flow.append({
                        'name': f'任务{i+1}',
                        'status': task_status,
                        'completed_at': completed_at.isoformat() if completed_at and task_status == 'completed' else None
                    })
            
            # 构建标题：教师姓名 + 模板名称
            title = f"{teacher_name}的{template_name}"
            
            # 插入新表
            cursor.execute("""
                INSERT INTO todo_items (
                    template_id, trigger_type, teacher_id, teacher_name,
                    title, description, status, priority, deadline,
                    created_at, completed_at, operator_id, task_flow,
                    total_tasks, completed_tasks, progress
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
                RETURNING id
            """, (
                new_template_id,
                'custom',
                teacher_code or str(teacher_id),
                teacher_name,
                title,
                remark,
                new_status,
                'normal',
                deadline,
                created_at or datetime.now(),
                completed_at,
                operator or 'system',
                json.dumps(task_flow) if task_flow else None,
                total_tasks or 0,
                completed_tasks or 0,
                progress or 0
            ))
            
            result = cursor.fetchone()
            if result:
                migrated_count += 1
        
        conn.commit()
        print(f"[OK] business_checklist_instances 迁移完成，共迁移 {migrated_count} 条记录")
        
    except Exception as e:
        conn.rollback()
        print(f"[ERROR] business_checklist_instances 迁移失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cursor.close()
        conn.close()

def migrate_from_todo_work_items():
    """从 todo_work_items 迁移数据"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        print("[OK] 开始从 todo_work_items 迁移数据...")
        
        # 查询旧表数据
        cursor.execute("""
            SELECT id, teacher_id, teacher_name, template_id, 
                   status, priority, due_date, created_at, 
                   completed_at, title, description
            FROM todo_work_items
            ORDER BY created_at DESC
        """)
        
        rows = cursor.fetchall()
        migrated_count = 0
        
        for row in rows:
            (old_id, teacher_id, teacher_name, template_id, 
             status, priority, due_date, created_at, 
             completed_at, title, description) = row
            
            # 映射状态
            status_map = {
                'pending': 'pending',
                'processing': 'in_progress',
                'completed': 'completed',
                'cancelled': 'returned'
            }
            new_status = status_map.get(status, 'pending')
            
            # 获取模板名称
            cursor.execute("SELECT 模板名称 FROM business_checklist_templates WHERE id = %s", (template_id,))
            template_result = cursor.fetchone()
            template_name = template_result[0] if template_result else '默认模板'
            
            # 查询新表中的模板ID
            cursor.execute("SELECT id FROM todo_templates WHERE template_name = %s", (template_name,))
            new_template_result = cursor.fetchone()
            new_template_id = new_template_result[0] if new_template_result else None
            
            # 如果没有找到模板，创建一个默认模板
            if not new_template_id:
                cursor.execute("""
                    INSERT INTO todo_templates (template_code, template_name, business_type, description, due_date_rule, is_enabled, created_at)
                    VALUES (%s, %s, 'CUSTOM', '自动迁移的模板', '7天', true, CURRENT_TIMESTAMP)
                    ON CONFLICT (template_code) DO NOTHING
                    RETURNING id
                """, (f"AUTO_TODO_{old_id}", template_name))
                result = cursor.fetchone()
                if result:
                    new_template_id = result[0]
            
            # 构建标题
            display_title = title or f"{teacher_name}的{template_name}"
            
            # 插入新表
            cursor.execute("""
                INSERT INTO todo_items (
                    template_id, trigger_type, teacher_id, teacher_name,
                    title, description, status, priority, deadline,
                    created_at, completed_at, operator_id, task_flow
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
                RETURNING id
            """, (
                new_template_id,
                'custom',
                teacher_id,
                teacher_name,
                display_title,
                description,
                new_status,
                priority or 'normal',
                due_date,
                created_at or datetime.now(),
                completed_at,
                'system',
                json.dumps([{'name': '处理待办', 'status': new_status, 'completed_at': completed_at.isoformat() if completed_at else None}])
            ))
            
            result = cursor.fetchone()
            if result:
                migrated_count += 1
        
        conn.commit()
        print(f"[OK] todo_work_items 迁移完成，共迁移 {migrated_count} 条记录")
        
    except Exception as e:
        conn.rollback()
        print(f"[ERROR] todo_work_items 迁移失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cursor.close()
        conn.close()

def migrate_templates():
    """迁移清单模板"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        print("[OK] 开始迁移清单模板...")
        
        # 从 business_checklist_templates 迁移
        cursor.execute("""
            SELECT id, 模板名称, 模板描述, 业务类型, 状态, 创建时间
            FROM business_checklist_templates
            WHERE 状态 = '启用'
        """)
        
        rows = cursor.fetchall()
        migrated_count = 0
        
        for row in rows:
            old_id, template_name, description, business_type, status, created_at = row
            
            # 映射业务类型
            trigger_type_map = {
                '退休': 'RETIREMENT',
                '死亡': 'DEATH',
                '80岁': 'OCTOGENARIAN',
                '到龄退休': 'RETIREMENT'
            }
            business_type_code = trigger_type_map.get(business_type, 'CUSTOM')
            
            # 插入新表
            cursor.execute("""
                INSERT INTO todo_templates (
                    template_code, template_name, business_type, description,
                    due_date_rule, is_enabled, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (template_code) DO NOTHING
                RETURNING id
            """, (
                f"MIGRATED_{old_id}",
                template_name,
                business_type_code,
                description,
                '7天',
                True,
                created_at or datetime.now()
            ))
            
            result = cursor.fetchone()
            if result:
                migrated_count += 1
        
        conn.commit()
        print(f"[OK] 清单模板迁移完成，共迁移 {migrated_count} 条记录")
        
    except Exception as e:
        conn.rollback()
        print(f"[ERROR] 清单模板迁移失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cursor.close()
        conn.close()

def main():
    """主函数"""
    print("="*60)
    print("[OK] 开始完整数据迁移")
    print("="*60)
    
    # 1. 迁移模板
    migrate_templates()
    
    # 2. 从 checklist_instances 迁移
    migrate_from_checklist_instances()
    
    # 3. 从 todo_work_items 迁移
    migrate_from_todo_work_items()
    
    print("="*60)
    print("[OK] 数据迁移完成")
    print("="*60)

if __name__ == '__main__':
    main()
