"""
将现有数据迁移到新的清单模板系统
- 死亡待办工作 → 清单模板
- 退休业务清单 → 清单模板
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
        print("开始数据迁移...")
        
        # 1. 迁移死亡待办工作为清单模板
        print("\n1. 迁移死亡待办工作...")
        
        cursor.execute("""
            INSERT INTO checklist_templates (模板名称, 模板描述, 适用对象, 状态)
            VALUES ('教师死亡后待办工作', '教师去世后需要办理的各项业务手续', '教师', '启用')
            RETURNING id
        """)
        death_template_id = cursor.fetchone()[0]
        print(f"   ✓ 创建死亡待办模板 (ID: {death_template_id})")
        
        # 添加触发条件：任职状态变更为"去世"
        cursor.execute("""
            INSERT INTO checklist_trigger_conditions 
            (模板ID, 条件名称, 条件类型, 条件字段, 操作符, 条件值, 排序)
            VALUES (%s, '任职状态变更为去世', 'status_change', 'employment_status', '变化为', '去世', 0)
        """, (death_template_id,))
        print(f"   ✓ 添加触发条件：任职状态变更为去世")
        
        # 添加任务项（11项任务）
        death_tasks = [
            ("收集死亡医学证明、火化证", "收集死亡医学证明、火化证等相关材料", None),
            ("登录养老系统打印终保承诺书", "登录养老保险系统打印终止保险承诺书", None),
            ("扫描上传材料", "扫描死亡医学证明、火化证、终保承诺书并上传养老系统", None),
            ("填报抚恤金审批表", "填报抚恤金、安葬费审批表", None),
            ("送审材料", "复印工资批复、死亡医学证明、火化证，与终保承诺书、抚恤金安葬费审批表一并送审", None),
            ("机关中心签批", "报到机关中心在火化证上签批未超领工资", None),
            ("工资科预审核", "报工资科预审核算结果", None),
            ("教育局审批", "报教育局审批签章", None),
            ("人社局审批", "报人社局工资科审批", None),
            ("财政局备案", "报财政局备案", None),
            ("处理绩效工资", "在绩效工资审批表中处理绩效，标明死亡信息", None)
        ]
        
        for idx, (task_name, task_desc, template_id) in enumerate(death_tasks, 1):
            cursor.execute("""
                INSERT INTO checklist_template_items 
                (模板ID, 任务序号, 任务名称, 任务说明, 是否必填, 关联文档模板ID, 办理时限天数, 时限提醒方式, 排序)
                VALUES (%s, %s, %s, %s, TRUE, %s, NULL, '截止前', %s)
            """, (death_template_id, idx, task_name, task_desc, template_id, idx - 1))
        
        print(f"   ✓ 添加11项死亡待办任务")
        
        # 2. 迁移退休业务清单为清单模板
        print("\n2. 迁移退休业务清单...")
        
        cursor.execute("""
            INSERT INTO checklist_templates (模板名称, 模板描述, 适用对象, 状态)
            VALUES ('教师退休业务清单', '教师退休时需要办理的各项业务手续', '教师', '启用')
            RETURNING id
        """)
        retirement_template_id = cursor.fetchone()[0]
        print(f"   ✓ 创建退休业务模板 (ID: {retirement_template_id})")
        
        # 添加触发条件：任职状态变更为"退休"
        cursor.execute("""
            INSERT INTO checklist_trigger_conditions 
            (模板ID, 条件名称, 条件类型, 条件字段, 操作符, 条件值, 排序)
            VALUES (%s, '任职状态变更为退休', 'status_change', 'employment_status', '变化为', '退休', 0)
        """, (retirement_template_id,))
        print(f"   ✓ 添加触发条件：任职状态变更为退休")
        
        # 添加触发条件：年龄满退休年龄（男60，女55）
        cursor.execute("""
            INSERT INTO checklist_trigger_conditions 
            (模板ID, 条件名称, 条件类型, 条件字段, 操作符, 条件值, 排序)
            VALUES (%s, '达到退休年龄', 'age', '年龄', '>=', '60', 1)
        """, (retirement_template_id,))
        print(f"   ✓ 添加触发条件：达到退休年龄")
        
        # 从现有的清单定义中获取任务项
        cursor.execute("""
            SELECT 清单名称, 任务项列表 
            FROM todo_work 
            WHERE 清单名称 LIKE '%退休%'
            LIMIT 1
        """)
        
        todo_row = cursor.fetchone()
        if todo_row and todo_row[1]:
            try:
                task_items = json.loads(todo_row[1]) if isinstance(todo_row[1], str) else todo_row[1]
                
                for idx, item in enumerate(task_items, 1):
                    task_name = item.get('标题', f'任务{idx}')
                    task_desc = item.get('说明', '')
                    
                    cursor.execute("""
                        INSERT INTO checklist_template_items 
                        (模板ID, 任务序号, 任务名称, 任务说明, 是否必填, 关联文档模板ID, 办理时限天数, 时限提醒方式, 排序)
                        VALUES (%s, %s, %s, %s, TRUE, NULL, NULL, '截止前', %s)
                    """, (retirement_template_id, idx, task_name, task_desc, idx - 1))
                
                print(f"   ✓ 添加{len(task_items)}项退休业务任务")
            except Exception as e:
                print(f"   ⚠ 解析退休任务项失败: {e}")
                # 添加默认任务项
                default_tasks = [
                    "填写退休申请表",
                    "提交身份证复印件",
                    "提交户口本复印件",
                    "办理工作交接",
                    "领取退休证"
                ]
                for idx, task_name in enumerate(default_tasks, 1):
                    cursor.execute("""
                        INSERT INTO checklist_template_items 
                        (模板ID, 任务序号, 任务名称, 任务说明, 是否必填, 关联文档模板ID, 办理时限天数, 时限提醒方式, 排序)
                        VALUES (%s, %s, %s, %s, TRUE, NULL, NULL, '截止前', %s)
                    """, (retirement_template_id, idx, task_name, '', idx - 1))
                print(f"   ✓ 添加{len(default_tasks)}项默认退休业务任务")
        else:
            print(f"   ⚠ 未找到现有退休任务数据")
        
        # 3. 迁移现有的死亡待办工作实例
        print("\n3. 迁移现有死亡待办实例...")
        
        cursor.execute("""
            SELECT id, 教师ID, 教师姓名, 身份证号码, 死亡日期, 状态, 完成进度, 创建时间, 完成时间
            FROM 教师死亡待办工作
        """)
        
        death_instances = cursor.fetchall()
        migrated_count = 0
        
        for row in death_instances:
            instance_id = row[0]
            teacher_id = row[1]
            teacher_name = row[2]
            id_card = row[3]
            death_date = row[4]
            status = row[5]
            progress = row[6] or 0
            created_at = row[7]
            completed_at = row[8]
            
            # 创建清单实例
            cursor.execute("""
                INSERT INTO checklist_instances 
                (模板ID, 关联对象ID, 关联对象类型, 关联对象名称, 触发条件详情, 状态, 完成进度, 创建时间, 完成时间)
                VALUES (%s, %s, '教师', %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                death_template_id,
                teacher_id,
                teacher_name,
                json.dumps({"死亡日期": death_date.isoformat() if death_date else None, "身份证号码": id_card}),
                '已完成' if status == '已完成' else '待处理',
                progress,
                created_at,
                completed_at
            ))
            
            new_instance_id = cursor.fetchone()[0]
            migrated_count += 1
            
            # 迁移任务处理记录
            cursor.execute("""
                SELECT 任务1_收集死亡证明, 任务2_打印终保承诺书, 任务3_扫描上传材料,
                       任务4_填报抚恤金审批表, 任务5_送审材料, 任务6_机关中心签批,
                       任务7_工资科预审核, 任务8_教育局审批, 任务9_人社局审批, 任务10_财政局备案,
                       任务11_处理绩效工资, 操作人, 操作时间
                FROM 教师死亡待办处理记录
                WHERE 待办ID = %s
                ORDER BY 操作时间 DESC
                LIMIT 1
            """, (instance_id,))
            
            process_row = cursor.fetchone()
            if process_row:
                # 获取任务项ID列表
                cursor.execute("""
                    SELECT id FROM checklist_template_items 
                    WHERE 模板ID = %s ORDER BY 任务序号
                """, (death_template_id,))
                
                item_ids = [r[0] for r in cursor.fetchall()]
                
                # 创建任务处理记录
                for task_idx, completed in enumerate(process_row[:11]):
                    if task_idx < len(item_ids) and completed:
                        cursor.execute("""
                            INSERT INTO checklist_item_records 
                            (实例ID, 任务项ID, 完成状态, 完成时间, 操作人)
                            VALUES (%s, %s, TRUE, %s, %s)
                        """, (new_instance_id, item_ids[task_idx], process_row[12] or created_at, process_row[11] or '系统'))
        
        print(f"   ✓ 迁移{migrated_count}个死亡待办实例")
        
        conn.commit()
        print("\n✅ 数据迁移完成！")
        print(f"\n迁移摘要:")
        print(f"  - 死亡待办模板 (ID: {death_template_id})")
        print(f"  - 退休业务模板 (ID: {retirement_template_id})")
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
