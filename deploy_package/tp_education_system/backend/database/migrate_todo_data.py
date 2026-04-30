#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
待办业务数据迁移脚本
将旧表数据迁移到新表
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

def migrate_checklist_instances():
    """迁移清单实例数据（待办数据）"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        print("[OK] 开始迁移清单实例数据...")
        
        # 查询旧表数据
        cursor.execute("""
            SELECT id, 模板ID, 关联对象ID, 关联对象名称, 关联对象编码,
                   状态, 创建时间, 截止时间, 实际完成时间, 处理人, 备注
            FROM business_checklist_instances
            ORDER BY 创建时间 DESC
        """)
        
        rows = cursor.fetchall()
        migrated_count = 0
        
        for row in rows:
            (old_id, template_id, teacher_id, teacher_name, teacher_code,
             status, created_at, deadline, completed_at, operator, remark) = row
            
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
                teacher_code or str(teacher_id),
                teacher_name,
                f"{teacher_name}的{template_name}",
                remark,
                new_status,
                'normal',
                deadline,
                created_at or datetime.now(),
                completed_at,
                operator or 'system',
                json.dumps([{'name': '处理待办', 'status': new_status, 'completed_at': completed_at.isoformat() if completed_at else None}])
            ))
            
            result = cursor.fetchone()
            if result:
                migrated_count += 1
        
        conn.commit()
        print(f"[OK] 清单实例数据迁移完成，共迁移 {migrated_count} 条记录")
        
    except Exception as e:
        conn.rollback()
        print(f"[ERROR] 清单实例数据迁移失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cursor.close()
        conn.close()

def migrate_checklist_templates():
    """迁移清单模板数据"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        print("[OK] 开始迁移清单模板数据...")
        
        # 查询旧表数据
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
                '退休': 'retirement',
                '死亡': 'death',
                '80岁': 'octogenarian',
                '到龄退休': 'retirement'
            }
            trigger_type = trigger_type_map.get(business_type, 'custom')
            
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
                trigger_type.upper(),
                description,
                '7天',
                True,
                created_at or datetime.now()
            ))
            
            result = cursor.fetchone()
            if result:
                migrated_count += 1
        
        conn.commit()
        print(f"[OK] 清单模板数据迁移完成，共迁移 {migrated_count} 条记录")
        
    except Exception as e:
        conn.rollback()
        print(f"[ERROR] 清单模板数据迁移失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cursor.close()
        conn.close()

def create_default_templates():
    """创建默认模板（如果没有数据）"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        print("[OK] 检查并创建默认模板...")
        
        # 检查是否已有模板
        cursor.execute("SELECT COUNT(*) FROM todo_templates")
        count = cursor.fetchone()[0]
        
        if count == 0:
            # 创建默认模板
            default_templates = [
                ('RETIREMENT_001', '到龄退休提醒', 'RETIREMENT', '教师到龄退休业务办理', '49天'),
                ('DEATH_001', '死亡登记', 'DEATH', '教师死亡登记业务', '7天'),
                ('OCTOGENARIAN_001', '80岁补贴申请', 'OCTOGENARIAN', '80周岁补贴申请业务', '60天'),
                ('RETIRE_REMIND_001', '退休提前提醒', 'RETIREMENT', '退休提前提醒', '49天')
            ]
            
            for code, name, business_type, description, due_rule in default_templates:
                cursor.execute("""
                    INSERT INTO todo_templates (
                        template_code, template_name, business_type, description,
                        due_date_rule, is_enabled, created_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                    ON CONFLICT (template_code) DO NOTHING
                """, (code, name, business_type, description, due_rule, True))
            
            conn.commit()
            print(f"[OK] 创建了 {len(default_templates)} 个默认模板")
        else:
            print(f"[OK] 已有 {count} 个模板")
        
    except Exception as e:
        conn.rollback()
        print(f"[ERROR] 创建默认模板失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cursor.close()
        conn.close()

def main():
    """主函数"""
    print("="*60)
    print("[OK] 开始待办业务数据迁移")
    print("="*60)
    
    # 1. 创建默认模板
    create_default_templates()
    
    # 2. 迁移旧模板数据
    migrate_checklist_templates()
    
    # 3. 迁移旧待办数据
    migrate_checklist_instances()
    
    print("="*60)
    print("[OK] 数据迁移完成")
    print("="*60)

if __name__ == '__main__':
    main()
