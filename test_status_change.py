#!/usr/bin/env python3
"""
测试状态变更流程
"""
import sys
sys.path.insert(0, r'd:\erp_thirteen\tp_education_system\backend')

import psycopg2
import json

def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        port="5432",
        database="taiping_education",
        user="taiping_user",
        password="taiping_password"
    )

def test_status_change():
    teacher_id = 273  # 使用王军峰测试
    teacher_name = "王军峰"
    target_status = "退休"
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        print("=== 开始测试状态变更 ===\n")
        
        # 1. 先检查教师当前状态
        cursor.execute("SELECT id, name, employment_status FROM teacher_basic_info WHERE id = %s", (teacher_id,))
        row = cursor.fetchone()
        print(f"1. 教师当前状态: ID={row[0]}, 姓名={row[1]}, 任职状态={row[2]}")
        
        # 2. 更新教师状态
        print(f"\n2. 更新教师状态为: {target_status}")
        cursor.execute("""
            UPDATE teacher_basic_info 
            SET employment_status = %s, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """, (target_status, teacher_id))
        print("   教师状态更新成功")
        
        # 3. 测试退休呈报表数据汇集
        print("\n3. 测试退休呈报表数据汇集...")
        
        # 查询教师基础信息
        cursor.execute("""
            SELECT id, name, id_card, archive_birth_date, ethnicity, 
                   native_place, work_start_date,
                   employment_status, contact_phone
            FROM teacher_basic_info 
            WHERE id = %s
        """, (teacher_id,))
        
        teacher_row = cursor.fetchone()
        print(f"   教师信息: ID={teacher_row[0]}, 姓名={teacher_row[1]}, 身份证={teacher_row[2]}")
        
        # 查询最高学历信息（通过身份证号关联）
        id_card = teacher_row[2] or ''
        cursor.execute("""
            SELECT education, graduate_date, graduate_school, major
            FROM teacher_education_record
            WHERE id_card = %s
            ORDER BY graduate_date DESC
            LIMIT 1
        """, (id_card,))
        
        education_row = cursor.fetchone()
        print(f"   学历信息: {education_row}")
        
        # 处理数据（id_card已经在上面获取）
        
        # 出生日期：优先使用档案出生日期，否则从身份证提取
        birth_date = teacher_row[3]  # archive_birth_date
        if not birth_date and len(id_card) == 18:
            try:
                birth_date = f"{id_card[6:10]}-{id_card[10:12]}-{id_card[12:14]}"
            except:
                pass
        print(f"   提取出生日期: {birth_date}")
        
        # 从身份证号提取性别
        gender = None
        if len(id_card) == 18:
            try:
                gender_code = int(id_card[16])
                gender = "男" if gender_code % 2 == 1 else "女"
            except:
                pass
        print(f"   提取性别: {gender}")
        
        # 计算工作年限
        work_years = 0
        if teacher_row[6]:
            try:
                from datetime import datetime
                start = datetime.strptime(str(teacher_row[6]), "%Y-%m-%d")
                today = datetime.now()
                work_years = today.year - start.year
                if (today.month, today.day) < (start.month, start.day):
                    work_years -= 1
            except:
                pass
        print(f"   计算工作年限: {work_years}")
        
        # 插入或更新退休呈报表数据中间表
        print("\n4. 执行SQL插入...")
        try:
            # 先检查是否已存在该教师的记录
            cursor.execute("""
                SELECT id FROM retirement_report_data WHERE teacher_id = %s
            """, (teacher_id,))
            
            existing_row = cursor.fetchone()
            
            if existing_row:
                # 更新现有记录
                cursor.execute("""
                    UPDATE retirement_report_data SET
                        姓名 = %s,
                        身份证号码 = %s,
                        性别 = %s,
                        出生日期 = %s,
                        民族 = %s,
                        文化程度 = %s,
                        参加工作时间 = %s,
                        工作年限 = %s,
                        籍贯 = %s,
                        现住址 = %s,
                        updated_at = NOW()
                    WHERE teacher_id = %s
                """, (
                    teacher_row[1],  # name
                    id_card,
                    gender,
                    birth_date,
                    teacher_row[4],  # ethnicity
                    education_row[0] if education_row else None,  # education
                    teacher_row[6],  # work_start_date
                    work_years,
                    teacher_row[5],  # native_place
                    None,  # current_address
                    teacher_id
                ))
                print("   SQL更新成功")
            else:
                # 插入新记录
                cursor.execute("""
                    INSERT INTO retirement_report_data (
                        teacher_id, 姓名, 身份证号码, 性别, 出生日期, 
                        民族, 文化程度, 参加工作时间, 工作年限,
                        籍贯, 现住址, created_at, updated_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                """, (
                    teacher_id,
                    teacher_row[1],  # name
                    id_card,
                    gender,
                    birth_date,
                    teacher_row[4],  # ethnicity
                    education_row[0] if education_row else None,  # education
                    teacher_row[6],  # work_start_date
                    work_years,
                    teacher_row[5],  # native_place
                    None  # current_address
                ))
                print("   SQL插入成功")
        except Exception as e:
            print(f"   SQL执行失败: {e}")
            import traceback
            traceback.print_exc()
            raise
        
        # 5. 创建待办工作
        print("\n5. 创建待办工作...")
        cursor.execute("""
            SELECT id, 清单名称, 任务项列表, 触发条件
            FROM business_checklist
            WHERE 是否有效 = true
        """)
        
        all_checklists = cursor.fetchall()
        print(f"   找到 {len(all_checklists)} 个有效清单模板")
        
        created_count = 0
        for checklist_row in all_checklists:
            checklist_id = checklist_row[0]
            checklist_name = checklist_row[1]
            task_items = checklist_row[2] if isinstance(checklist_row[2], list) else json.loads(checklist_row[2]) if checklist_row[2] else []
            trigger_condition = checklist_row[3] if isinstance(checklist_row[3], dict) else json.loads(checklist_row[3]) if checklist_row[3] else {}
            
            target_statuses = trigger_condition.get("target_status", [])
            if isinstance(target_statuses, str):
                target_statuses = [target_statuses]
            
            if target_status in target_statuses:
                # 检查是否已存在该待办
                cursor.execute("""
                    SELECT id FROM todo_work_items
                    WHERE 教师ID = %s AND 清单ID = %s AND 状态 = 'pending'
                """, (teacher_id, checklist_id))
                
                if not cursor.fetchone():
                    # 创建待办工作
                    total_tasks = len(task_items)
                    cursor.execute("""
                        INSERT INTO todo_work_items 
                        (教师ID, 清单ID, 清单名称, 教师姓名, 任务项列表, 总任务数, 已完成数, 状态)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        RETURNING id
                    """, (
                        teacher_id,
                        checklist_id,
                        checklist_name,
                        teacher_name,
                        json.dumps(task_items),
                        total_tasks,
                        0,
                        "pending"
                    ))
                    
                    todo_id = cursor.fetchone()[0]
                    created_count += 1
                    print(f"   创建待办: {checklist_name} (ID: {todo_id})")
        
        print(f"   共创建 {created_count} 个待办")
        
        # 提交事务
        conn.commit()
        print("\n✅ 事务提交成功！")
        
        # 验证结果
        print("\n6. 验证结果...")
        cursor.execute("SELECT employment_status FROM teacher_basic_info WHERE id = %s", (teacher_id,))
        new_status = cursor.fetchone()[0]
        print(f"   教师新状态: {new_status}")
        
        cursor.execute("SELECT 姓名 FROM retirement_report_data WHERE teacher_id = %s", (teacher_id,))
        retirement_data = cursor.fetchone()
        if retirement_data:
            print(f"   退休呈报表数据: 姓名={retirement_data[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM todo_work_items WHERE 教师ID = %s AND 状态 = 'pending'", (teacher_id,))
        todo_count = cursor.fetchone()[0]
        print(f"   待办工作数量: {todo_count}")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    test_status_change()
