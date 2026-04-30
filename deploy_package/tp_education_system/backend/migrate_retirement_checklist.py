"""
将现有的退休业务清单数据迁移到统一清单系统
- 源表: business_checklist (ID=1, 退休教师呈报业务清单)
- 目标表: business_checklist_templates 和 business_checklist_items
"""
import psycopg2
import json
import sys

DATABASE_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "database": "taiping_education",
    "user": "taiping_user",
    "password": "taiping_password"
}

def get_db_connection():
    return psycopg2.connect(**DATABASE_CONFIG)

def migrate():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        print("=== 迁移退休业务清单到统一清单系统 ===\n")
        
        # 1. 获取现有的退休业务清单数据
        print("1. 读取现有退休业务清单数据...")
        cursor.execute("""
            SELECT id, 清单名称, 触发条件, 任务项列表, 是否有效
            FROM business_checklist
            WHERE id = 1
        """)
        
        row = cursor.fetchone()
        if not row:
            print("   ❌ 未找到ID=1的退休业务清单")
            return
        
        checklist_id = row[0]
        checklist_name = row[1]
        trigger_conditions = row[2]
        task_items = row[3]
        is_valid = row[4]
        
        print(f"   ✓ 找到清单: {checklist_name}")
        
        # 解析任务项
        if task_items:
            tasks = task_items if isinstance(task_items, list) else json.loads(task_items)
            print(f"   ✓ 任务项数量: {len(tasks)}")
        else:
            tasks = []
            print("   ⚠ 没有任务项")
        
        # 2. 更新统一清单系统中的退休模板
        print("\n2. 更新统一清单系统模板...")
        
        # 检查是否已有退休模板
        cursor.execute("""
            SELECT id FROM business_checklist_templates
            WHERE 业务类型 = 'RETIREMENT' AND 模板编码 = 'RETIREMENT_001'
        """)
        
        existing = cursor.fetchone()
        
        if existing:
            template_id = existing[0]
            # 更新现有模板
            cursor.execute("""
                UPDATE business_checklist_templates
                SET 模板名称 = %s,
                    模板描述 = %s,
                    触发条件配置 = %s,
                    状态 = %s,
                    更新时间 = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (
                checklist_name,
                '教师退休时需要办理的各项业务手续（从原有系统迁移）',
                json.dumps([{
                    "条件类型": "employment_status",
                    "条件字段": "employment_status",
                    "操作符": "变化为",
                    "条件值": "退休",
                    "条件名称": "任职状态变更为退休"
                }]),
                '启用' if is_valid else '停用',
                template_id
            ))
            print(f"   ✓ 更新模板 ID: {template_id}")
            
            # 删除旧的模板任务项
            cursor.execute("""
                DELETE FROM business_checklist_items
                WHERE 模板ID = %s
            """, (template_id,))
            print(f"   ✓ 删除旧的任务项")
        else:
            # 创建新模板
            cursor.execute("""
                INSERT INTO business_checklist_templates 
                (模板编码, 模板名称, 模板描述, 适用对象类型, 业务类型, 状态, 触发条件配置, 自动推送, 创建人)
                VALUES ('RETIREMENT_001', %s, %s, '教师', 'RETIREMENT', %s, %s, TRUE, '系统迁移')
                RETURNING id
            """, (
                checklist_name,
                '教师退休时需要办理的各项业务手续（从原有系统迁移）',
                '启用' if is_valid else '停用',
                json.dumps([{
                    "条件类型": "employment_status",
                    "条件字段": "employment_status",
                    "操作符": "变化为",
                    "条件值": "退休",
                    "条件名称": "任职状态变更为退休"
                }])
            ))
            template_id = cursor.fetchone()[0]
            print(f"   ✓ 创建新模板 ID: {template_id}")
        
        # 3. 迁移任务项
        print("\n3. 迁移任务项...")
        
        for idx, task in enumerate(tasks, 1):
            task_name = task.get('标题', f'任务{idx}')
            task_desc = task.get('参数', {}).get('说明', '')
            task_type = task.get('类型', '普通任务')
            task_target = task.get('目标', '')
            task_params = task.get('参数', {})
            
            # 根据任务类型设置不同的时限
            deadline_days = None
            if '呈报表' in task_name or '申领表' in task_name:
                deadline_days = 7
            elif '职务升级' in task_name:
                deadline_days = 15
            elif '绩效' in task_name:
                deadline_days = 30
            elif '上传' in task_name:
                deadline_days = 20
            elif '退休证' in task_name:
                deadline_days = 45
            
            cursor.execute("""
                INSERT INTO business_checklist_items 
                (模板ID, 任务序号, 任务编码, 任务名称, 任务说明, 是否必填, 
                 办理时限天数, 时限计算方式, 提醒方式, 排序, 关联数据字段)
                VALUES (%s, %s, %s, %s, %s, TRUE, %s, '清单创建后', '截止前', %s, %s)
            """, (
                template_id,
                idx,
                f"RETIREMENT_001_TASK{idx:03d}",
                task_name,
                task_desc,
                deadline_days,
                idx - 1,
                json.dumps({
                    '原任务类型': task_type,
                    '原任务目标': task_target,
                    '原任务参数': task_params
                })
            ))
            
            print(f"   ✓ 添加任务 {idx}: {task_name}")
        
        # 4. 更新 business_checklist 表的关联模板ID
        print("\n4. 更新原清单的关联模板ID...")
        cursor.execute("""
            UPDATE business_checklist
            SET "关联模板ID" = %s,
                是否有效 = FALSE
            WHERE id = %s
        """, (str(template_id), checklist_id))
        print(f"   ✓ 原清单(ID={checklist_id})已关联到新模板(ID={template_id})并标记为无效")
        
        # 5. 迁移现有的todo_work实例
        print("\n5. 迁移现有的待办实例...")
        cursor.execute("""
            SELECT id, 教师ID, 教师姓名, 任务项列表, 总任务数, 已完成数, 状态, created_at, completed_at
            FROM todo_work
            WHERE 清单ID = %s
        """, (checklist_id,))
        
        todo_instances = cursor.fetchall()
        migrated_count = 0
        
        for todo in todo_instances:
            todo_id = todo[0]
            teacher_id = todo[1]
            teacher_name = todo[2]
            todo_tasks = todo[3]
            total_tasks = todo[4] or 0
            completed_tasks = todo[5] or 0
            status = todo[6]
            created_at = todo[7]
            completed_at = todo[8]
            
            # 计算进度
            progress = int((completed_tasks / total_tasks) * 100) if total_tasks > 0 else 0
            
            # 生成实例编码
            instance_code = f"RETIREMENT_001_{teacher_id}_{created_at.strftime('%Y%m%d%H%M%S') if created_at else '00000000000000'}"
            
            # 检查是否已存在
            cursor.execute("""
                SELECT id FROM business_checklist_instances
                WHERE 实例编码 = %s
            """, (instance_code,))
            
            if cursor.fetchone():
                continue
            
            # 创建清单实例
            cursor.execute("""
                INSERT INTO business_checklist_instances 
                (模板ID, 实例编码, 关联对象ID, 关联对象类型, 关联对象名称,
                 触发事件, 状态, 完成进度, 总任务数, 已完成数, 创建时间, 截止时间, 实际完成时间)
                VALUES (%s, %s, %s, '教师', %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                template_id,
                instance_code,
                teacher_id,
                teacher_name,
                json.dumps({"原todo_work_id": todo_id}),
                '已完成' if status == 'completed' else '待处理',
                progress,
                len(tasks),
                completed_tasks,
                created_at,
                created_at + psycopg2.extensions.DateFromTicks(30 * 24 * 3600) if created_at else None,
                completed_at
            ))
            
            instance_id = cursor.fetchone()[0]
            migrated_count += 1
            
            # 迁移任务处理记录
            if todo_tasks:
                try:
                    todo_task_list = todo_tasks if isinstance(todo_tasks, list) else json.loads(todo_tasks)
                    
                    # 获取新模板的任务项ID
                    cursor.execute("""
                        SELECT id FROM business_checklist_items
                        WHERE 模板ID = %s
                        ORDER BY 任务序号
                    """, (template_id,))
                    
                    new_item_ids = [r[0] for r in cursor.fetchall()]
                    
                    for task_idx, todo_task in enumerate(todo_task_list):
                        if task_idx < len(new_item_ids):
                            is_completed = todo_task.get('完成状态', False)
                            if is_completed:
                                cursor.execute("""
                                    INSERT INTO business_checklist_item_records 
                                    (实例ID, 任务项ID, 任务名称, 完成状态, 完成时间, 操作人)
                                    VALUES (%s, %s, %s, '已完成', %s, '系统迁移')
                                """, (
                                    instance_id,
                                    new_item_ids[task_idx],
                                    todo_task.get('标题', f'任务{task_idx+1}'),
                                    completed_at or created_at
                                ))
                except Exception as e:
                    print(f"   ⚠ 迁移任务记录失败 (todo_id={todo_id}): {e}")
        
        print(f"   ✓ 迁移 {migrated_count} 个待办实例")
        
        conn.commit()
        print("\n✅ 数据迁移完成！")
        print(f"\n迁移摘要:")
        print(f"  - 退休业务模板 ID: {template_id}")
        print(f"  - 任务项数量: {len(tasks)}")
        print(f"  - 迁移实例数: {migrated_count}")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ 迁移失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    migrate()
