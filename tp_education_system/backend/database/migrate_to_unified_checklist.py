"""
将现有清单数据迁移到统一清单业务系统
整合：退休业务清单、死亡待办、高龄提醒等
"""
import psycopg2
import json
import sys
from datetime import datetime, timedelta

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
        print("=== 迁移数据到统一清单业务系统 ===\n")
        
        # 1. 创建退休业务清单模板
        print("1. 创建退休业务清单模板...")
        cursor.execute("""
            INSERT INTO business_checklist_templates 
            (模板编码, 模板名称, 模板描述, 适用对象类型, 业务类型, 状态, 触发条件配置, 自动推送, 创建人)
            VALUES ('RETIREMENT_001', '教师退休业务清单', '教师退休时需要办理的各项业务手续', '教师', 'RETIREMENT', '启用', 
                    '[{"条件类型": "employment_status", "条件字段": "employment_status", "操作符": "变化为", "条件值": "退休", "条件名称": "任职状态变更为退休"}]',
                    TRUE, '系统迁移')
            RETURNING id
        """)
        retirement_template_id = cursor.fetchone()[0]
        print(f"   ✓ 退休模板ID: {retirement_template_id}")
        
        # 添加退休任务项
        retirement_tasks = [
            ("填写退休申请表", "填写完整的退休申请表格", 7),
            ("提交身份证复印件", "提供本人身份证复印件2份", 3),
            ("提交户口本复印件", "提供户口本首页和本人页复印件", 3),
            ("工作交接", "完成工作交接手续", 15),
            ("领取退休证", "到人事部门领取退休证", 30),
            ("办理社保转移", "办理养老保险关系转移", 30),
            ("公积金提取", "办理住房公积金提取或转移", 30)
        ]
        
        for idx, (name, desc, days) in enumerate(retirement_tasks, 1):
            cursor.execute("""
                INSERT INTO business_checklist_items 
                (模板ID, 任务序号, 任务编码, 任务名称, 任务说明, 是否必填, 办理时限天数, 时限计算方式, 提醒方式, 排序)
                VALUES (%s, %s, %s, %s, %s, TRUE, %s, '清单创建后', '截止前', %s)
            """, (retirement_template_id, idx, f"RETIREMENT_001_TASK{idx:03d}", name, desc, days, idx - 1))
        
        print(f"   ✓ 添加{len(retirement_tasks)}项退休任务")
        
        # 2. 创建死亡业务清单模板
        print("\n2. 创建死亡业务清单模板...")
        cursor.execute("""
            INSERT INTO business_checklist_templates 
            (模板编码, 模板名称, 模板描述, 适用对象类型, 业务类型, 状态, 触发条件配置, 自动推送, 创建人)
            VALUES ('DEATH_001', '教师死亡后待办工作', '教师去世后需要办理的各项业务手续', '教师', 'DEATH', '启用',
                    '[{"条件类型": "employment_status", "条件字段": "employment_status", "操作符": "变化为", "条件值": "去世", "条件名称": "任职状态变更为去世"}]',
                    TRUE, '系统迁移')
            RETURNING id
        """)
        death_template_id = cursor.fetchone()[0]
        print(f"   ✓ 死亡模板ID: {death_template_id}")
        
        # 添加死亡任务项（11项）
        death_tasks = [
            ("收集死亡医学证明、火化证", "收集死亡医学证明、火化证等相关材料", 3),
            ("登录养老系统打印终保承诺书", "登录养老保险系统打印终止保险承诺书", 5),
            ("扫描上传材料", "扫描死亡医学证明、火化证、终保承诺书并上传养老系统", 7),
            ("填报抚恤金审批表", "填报抚恤金、安葬费审批表", 10),
            ("送审材料", "复印工资批复、死亡医学证明、火化证，与终保承诺书、抚恤金安葬费审批表一并送审", 15),
            ("机关中心签批", "报到机关中心在火化证上签批未超领工资", 20),
            ("工资科预审核", "报工资科预审核算结果", 25),
            ("教育局审批", "报教育局审批签章", 30),
            ("人社局审批", "报人社局工资科审批", 35),
            ("财政局备案", "报财政局备案", 40),
            ("处理绩效工资", "在绩效工资审批表中处理绩效，标明死亡信息", 45)
        ]
        
        for idx, (name, desc, days) in enumerate(death_tasks, 1):
            cursor.execute("""
                INSERT INTO business_checklist_items 
                (模板ID, 任务序号, 任务编码, 任务名称, 任务说明, 是否必填, 办理时限天数, 时限计算方式, 提醒方式, 排序)
                VALUES (%s, %s, %s, %s, %s, TRUE, %s, '清单创建后', '截止前', %s)
            """, (death_template_id, idx, f"DEATH_001_TASK{idx:03d}", name, desc, days, idx - 1))
        
        print(f"   ✓ 添加{len(death_tasks)}项死亡任务")
        
        # 3. 创建高龄提醒清单模板
        print("\n3. 创建高龄提醒清单模板...")
        cursor.execute("""
            INSERT INTO business_checklist_templates 
            (模板编码, 模板名称, 模板描述, 适用对象类型, 业务类型, 状态, 触发条件配置, 自动推送, 创建人)
            VALUES ('OCTOGENARIAN_001', '80周岁高龄补贴办理', '教师满80周岁时办理高龄补贴相关手续', '教师', 'OCTOGENARIAN', '启用',
                    '[{"条件类型": "age", "条件字段": "birth_date", "操作符": ">=", "条件值": "80", "条件名称": "年龄满80周岁"}]',
                    TRUE, '系统迁移')
            RETURNING id
        """)
        octo_template_id = cursor.fetchone()[0]
        print(f"   ✓ 高龄模板ID: {octo_template_id}")
        
        # 添加高龄任务项
        octo_tasks = [
            ("提交高龄补贴申请", "填写并提交高龄补贴申请表", 30),
            ("提交身份证复印件", "提供本人身份证复印件", 30),
            ("提交户口本复印件", "提供户口本复印件", 30),
            ("提交银行卡信息", "提供用于接收补贴的银行卡信息", 30),
            ("社区审核", "到所在社区进行审核盖章", 45)
        ]
        
        for idx, (name, desc, days) in enumerate(octo_tasks, 1):
            cursor.execute("""
                INSERT INTO business_checklist_items 
                (模板ID, 任务序号, 任务编码, 任务名称, 任务说明, 是否必填, 办理时限天数, 时限计算方式, 提醒方式, 排序)
                VALUES (%s, %s, %s, %s, %s, TRUE, %s, '清单创建后', '截止前', %s)
            """, (octo_template_id, idx, f"OCTOGENARIAN_001_TASK{idx:03d}", name, desc, days, idx - 1))
        
        print(f"   ✓ 添加{len(octo_tasks)}项高龄任务")
        
        # 4. 迁移现有的死亡待办实例
        print("\n4. 迁移现有死亡待办实例...")
        cursor.execute("""
            SELECT id, 教师ID, 教师姓名, 身份证号码, 死亡日期, 状态, 完成进度, 创建时间, 完成时间
            FROM 教师死亡待办工作
        """)
        
        death_instances = cursor.fetchall()
        migrated_death = 0
        
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
            
            instance_code = f"DEATH_001_{teacher_id}_{created_at.strftime('%Y%m%d%H%M%S')}"
            
            cursor.execute("""
                INSERT INTO business_checklist_instances 
                (模板ID, 实例编码, 关联对象ID, 关联对象类型, 关联对象名称, 关联对象编码,
                 触发事件, 状态, 完成进度, 总任务数, 已完成数, 创建时间, 截止时间, 实际完成时间)
                VALUES (%s, %s, %s, '教师', %s, %s, %s, %s, %s, 11, %s, %s, %s, %s)
                RETURNING id
            """, (
                death_template_id, instance_code, teacher_id, teacher_name, id_card,
                json.dumps({"死亡日期": death_date.isoformat() if death_date else None}),
                '已完成' if status == '已完成' else '待处理',
                progress,
                int(progress / 100 * 11),
                created_at,
                created_at + timedelta(days=45),
                completed_at
            ))
            
            new_instance_id = cursor.fetchone()[0]
            migrated_death += 1
        
        print(f"   ✓ 迁移{migrated_death}个死亡待办实例")
        
        # 5. 从todo_work表迁移退休业务清单
        print("\n5. 迁移退休业务清单实例...")
        cursor.execute("""
            SELECT id, 教师ID, 教师姓名, 清单名称, 任务项列表, 总任务数, 已完成数, 状态, created_at, completed_at
            FROM todo_work
            WHERE 清单名称 LIKE '%退休%'
        """)
        
        todo_instances = cursor.fetchall()
        migrated_todo = 0
        
        for row in todo_instances:
            todo_id = row[0]
            teacher_id = row[1]
            teacher_name = row[2]
            checklist_name = row[3]
            task_items = row[4]
            total_tasks = row[5] or 0
            completed_tasks = row[6] or 0
            status = row[7]
            created_at = row[8]
            completed_at = row[9]
            
            instance_code = f"RETIREMENT_001_{teacher_id}_{created_at.strftime('%Y%m%d%H%M%S')}"
            progress = int((completed_tasks / total_tasks) * 100) if total_tasks > 0 else 0
            
            cursor.execute("""
                INSERT INTO business_checklist_instances 
                (模板ID, 实例编码, 关联对象ID, 关联对象类型, 关联对象名称,
                 触发事件, 状态, 完成进度, 总任务数, 已完成数, 创建时间, 截止时间, 实际完成时间)
                VALUES (%s, %s, %s, '教师', %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                retirement_template_id, instance_code, teacher_id, teacher_name,
                json.dumps({"原清单名称": checklist_name}),
                '已完成' if status == '已完成' else '待处理',
                progress, 7, completed_tasks,
                created_at,
                created_at + timedelta(days=30),
                completed_at
            ))
            
            new_instance_id = cursor.fetchone()[0]
            migrated_todo += 1
        
        print(f"   ✓ 迁移{migrated_todo}个退休业务清单实例")
        
        conn.commit()
        print("\n✅ 数据迁移完成！")
        print(f"\n迁移摘要:")
        print(f"  - 退休业务模板 (ID: {retirement_template_id})")
        print(f"  - 死亡业务模板 (ID: {death_template_id})")
        print(f"  - 高龄补贴模板 (ID: {octo_template_id})")
        print(f"  - 迁移死亡实例: {migrated_death}个")
        print(f"  - 迁移退休实例: {migrated_todo}个")
        
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
