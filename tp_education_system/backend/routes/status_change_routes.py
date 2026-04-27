"""
状态变更处理路由
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import psycopg2
import json
from datetime import datetime
import sys
import os

# 添加 utils 目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.dict_utils import get_education_name

router = APIRouter(prefix="/api/status-change", tags=["status-change"])

DATABASE_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "database": "taiping_education",
    "user": "taiping_user",
    "password": "taiping_password"
}


def get_db_connection():
    return psycopg2.connect(**DATABASE_CONFIG)


def create_trigger_event(teacher_id: int, teacher_name: str, old_status: str, new_status: str, template_code: str = None):
    """创建待办清单（自动确认，无需手动确认）
    返回: (success: bool, message: str, existing_todo_id: int or None)
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    trigger_reason = f'教师 {teacher_name} 的任职状态从 "{old_status}" 变为 "{new_status}"'
    
    # 优先从 business_checklist 表获取用户配置的任务项
    cursor.execute("""
        SELECT id, 清单名称, 任务项列表
        FROM business_checklist 
        WHERE 触发条件::text LIKE %s
        LIMIT 1
    """, (f'%{new_status}%',))
    checklist = cursor.fetchone()
    
    if checklist:
        checklist_id, template_name, task_items = checklist
        
        # 检查是否已存在相同待办（相同template_id + teacher_id + pending状态）
        cursor.execute("""
            SELECT id, status FROM todo_items 
            WHERE teacher_id = %s AND template_id = %s AND status = 'pending'
        """, (teacher_id, str(checklist_id)))
        existing = cursor.fetchone()
        
        if existing:
            print(f"[触发] 跳过：教师{teacher_name}已有相同待办(ID:{existing[0]})")
            cursor.close()
            conn.close()
            return (False, "已存在相同待办", existing[0])
        
        # 解析任务项列表
        if isinstance(task_items, str):
            try:
                task_items = json.loads(task_items)
            except:
                task_items = []
        
        # 截止日期默认为30天
        due_date_rule = 30
        
        # 计算截止日期
        due_date = None
        try:
            from datetime import timedelta
            due_date = datetime.now().date() + timedelta(days=due_date_rule)
        except:
            pass
        
        # 获取业务类型
        business_type = 'RETIREMENT'
        
        # 将task_items转为JSON字符串
        task_items_json = json.dumps(task_items) if task_items else '[]'
        
        # 创建待办事项
        cursor.execute("""
            INSERT INTO todo_items (
                template_id, business_type, teacher_id, teacher_name,
                title, description, status, priority, due_date, task_items,
                created_by, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            str(checklist_id),
            business_type,
            teacher_id,
            teacher_name,
            f"{template_name} - {teacher_name}",
            trigger_reason,
            'pending',
            'normal',
            due_date,
            task_items_json,
            'system',
            datetime.now()
        ))
        
        todo_id = cursor.fetchone()[0]
        conn.commit()
        print(f"[触发] 从business_checklist创建待办: ID={todo_id}, 教师={teacher_name}, 清单={template_name}")
        cursor.close()
        conn.close()
        return (True, "创建成功", todo_id)
    
    # 如果business_checklist没有，尝试从todo_templates获取
    if not template_code:
        cursor.execute("""
            SELECT template_code FROM trigger_conditions 
            WHERE listen_table = 'teacher_basic_info' 
              AND listen_field = 'employment_status'
              AND trigger_value = %s
              AND is_enabled = true
            LIMIT 1
        """, (new_status,))
        result = cursor.fetchone()
        if result:
            template_code = result[0]
    
    if not template_code:
        print(f"[触发] 没有找到模板代码，跳过创建待办: {trigger_reason}")
        cursor.close()
        conn.close()
        return
    
    # 获取模板详情
    cursor.execute("""
        SELECT template_name, task_flow, due_date_rule
        FROM todo_templates
        WHERE template_code = %s
    """, (template_code,))
    template = cursor.fetchone()
    
    if not template:
        print(f"[触发] 没有找到模板: {template_code}")
        cursor.close()
        conn.close()
        return
    
    template_name, task_flow, due_date_rule = template
    
    # 计算截止日期
    due_date = None
    if due_date_rule:
        try:
            from datetime import timedelta
            days = int(due_date_rule)
            due_date = datetime.now().date() + timedelta(days=days)
        except:
            pass
    
    # 获取业务类型
    business_type = template_code.split('_')[0] if template_code else 'CUSTOM'
    
    # 将task_flow转为JSON字符串
    task_flow_json = json.dumps(task_flow) if task_flow else '[]'
    
    # 创建待办事项
    cursor.execute("""
        INSERT INTO todo_items (
            template_id, business_type, teacher_id, teacher_name,
            title, description, status, priority, due_date, task_items,
            created_by, created_at
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
    """, (
        template_code,
        business_type,
        teacher_id,
        teacher_name,
        f"{template_name} - {teacher_name}",
        trigger_reason,
        'pending',
        'normal',
        due_date,
        task_flow_json,
        'system',
        datetime.now()
    ))
    
    todo_id = cursor.fetchone()[0]
    
    conn.commit()
    print(f"[触发] 从todo_templates创建待办: ID={todo_id}, 教师={teacher_name}, 模板={template_code}")
    
    cursor.close()
    conn.close()


@router.post("/process")
async def process_status_change(data: Dict[str, Any]):
    """
    处理教师状态变更
    当状态变更为退休时，自动汇集退休呈报表数据并创建待办工作清单
    """
    try:
        teacher_id = data.get("teacher_id")
        teacher_name = data.get("teacher_name")
        source_status = data.get("source_status")
        target_status = data.get("target_status")
        
        if not teacher_id or not target_status:
            raise HTTPException(status_code=400, detail="缺少必要参数")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 获取变更前的状态和教师姓名
        cursor.execute("""
            SELECT employment_status, name FROM teacher_basic_info WHERE id = %s
        """, (teacher_id,))
        row = cursor.fetchone()
        old_status = row[0] if row else None
        teacher_name = data.get("teacher_name") or (row[1] if row else "未知")
        
        # 更新教师状态
        cursor.execute("""
            UPDATE teacher_basic_info 
            SET employment_status = %s, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """, (target_status, teacher_id))
        
        conn.commit()
        
        # 实时触发提醒
        if old_status and old_status != target_status:
            create_trigger_event(teacher_id, teacher_name, old_status, target_status)
        
        # 如果状态变更为退休，自动汇集退休呈报表数据
        data_collection_error = None
        if target_status == '退休':
            try:
                # 查询教师基础信息
                cursor.execute("""
                    SELECT id, name, id_card, archive_birth_date, ethnicity, 
                           native_place, work_start_date,
                           employment_status, contact_phone
                    FROM teacher_basic_info 
                    WHERE id = %s
                """, (teacher_id,))
                
                teacher_row = cursor.fetchone()
                if teacher_row:
                    # 获取身份证号
                    id_card = teacher_row[2]  # id_card
                    
                    # 查询最高学历信息（通过 teacher_id 关联）
                    cursor.execute("""
                        SELECT education, graduate_date, graduate_school, major
                        FROM teacher_education_record
                        WHERE teacher_id = %s
                        ORDER BY graduate_date DESC
                        LIMIT 1
                    """, (teacher_id,))
                    
                    education_row = cursor.fetchone()
                    
                    # 处理数据
                    
                    # 出生日期：优先使用档案出生日期，否则从身份证提取
                    birth_date = teacher_row[3]  # archive_birth_date
                    if not birth_date and id_card and len(id_card) == 18:
                        try:
                            birth_date = f"{id_card[6:10]}-{id_card[10:12]}-{id_card[12:14]}"
                        except:
                            pass
                    
                    # 从身份证号提取性别
                    gender = None
                    if id_card and len(id_card) == 18:
                        try:
                            gender_code = int(id_card[16])
                            gender = "男" if gender_code % 2 == 1 else "女"
                        except:
                            pass
                    
                    # 计算工作年限
                    work_years = 0
                    if teacher_row[6]:  # work_start_date
                        try:
                            from datetime import datetime
                            start = datetime.strptime(str(teacher_row[6]), "%Y-%m-%d")
                            today = datetime.now()
                            work_years = today.year - start.year
                            if (today.month, today.day) < (start.month, start.day):
                                work_years -= 1
                        except:
                            pass
                    
                    # 收集扩展数据（职务、岗位等）
                    # 从现有表查询数据，没有则保持为空
                    extended_data = {
                        '职务': None,  # 从现有表查询，没有就为空
                        '岗位': None,  # 从现有表查询，没有就为空
                        '技术职称': None,  # 从现有表查询，没有就为空
                        '退休原因': None,  # 从现有表查询，没有就为空
                        '退休后居住地址': None,
                        '退休时间': None,  # 从现有表查询，没有就为空
                        '单位意见': None,
                        '证明人及其住址': None,
                        '直系亲属信息': None,
                        '是否独生子女': None,  # 从现有表查询，没有就为空
                        '入党年月': None,  # 从现有表查询，没有就为空
                        '薪级工资': None,
                        '岗位工资': None,
                        '技术等级': None,
                    }
                    
                    # 插入或更新退休呈报表数据中间表（使用中文字段名）
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
                                职务 = %s,
                                岗位 = %s,
                                技术职称 = %s,
                                退休原因 = %s,
                                退休后居住地址 = %s,
                                退休时间 = %s,
                                单位意见 = %s,
                                证明人及其住址 = %s,
                                直系亲属信息 = %s,
                                是否独生子女 = %s,
                                入党年月 = %s,
                                薪级工资 = %s,
                                岗位工资 = %s,
                                技术等级 = %s,
                                updated_at = NOW()
                            WHERE teacher_id = %s
                        """, (
                            teacher_row[1],  # name
                            id_card,
                            gender,
                            birth_date,
                            teacher_row[4],  # ethnicity
                            get_education_name(education_row[0], DATABASE_CONFIG) if education_row else None,  # education - 转换为中文
                            teacher_row[6],  # work_start_date
                            work_years,
                            teacher_row[5],  # native_place
                            None,  # current_address
                            extended_data['职务'],
                            extended_data['岗位'],
                            extended_data['技术职称'],
                            extended_data['退休原因'],
                            extended_data['退休后居住地址'],
                            extended_data['退休时间'],
                            extended_data['单位意见'],
                            extended_data['证明人及其住址'],
                            extended_data['直系亲属信息'],
                            extended_data['是否独生子女'],
                            extended_data['入党年月'],
                            extended_data['薪级工资'],
                            extended_data['岗位工资'],
                            extended_data['技术等级'],
                            teacher_id
                        ))
                    else:
                        # 插入新记录
                        cursor.execute("""
                            INSERT INTO retirement_report_data (
                                teacher_id, 姓名, 身份证号码, 性别, 出生日期, 
                                民族, 文化程度, 参加工作时间, 工作年限,
                                籍贯, 现住址, 职务, 岗位, 技术职称,
                                退休原因, 退休后居住地址, 退休时间, 单位意见,
                                证明人及其住址, 直系亲属信息, 是否独生子女,
                                入党年月, 薪级工资, 岗位工资, 技术等级,
                                created_at, updated_at
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                        """, (
                            teacher_id,
                            teacher_row[1],  # name
                            id_card,
                            gender,
                            birth_date,
                            teacher_row[4],  # ethnicity
                            get_education_name(education_row[0], DATABASE_CONFIG) if education_row else None,  # education - 转换为中文
                            teacher_row[6],  # work_start_date
                            work_years,
                            teacher_row[5],  # native_place
                            None,  # current_address
                            extended_data['职务'],
                            extended_data['岗位'],
                            extended_data['技术职称'],
                            extended_data['退休原因'],
                            extended_data['退休后居住地址'],
                            extended_data['退休时间'],
                            extended_data['单位意见'],
                            extended_data['证明人及其住址'],
                            extended_data['直系亲属信息'],
                            extended_data['是否独生子女'],
                            extended_data['入党年月'],
                            extended_data['薪级工资'],
                            extended_data['岗位工资'],
                            extended_data['技术等级'],
                        ))
                    
                    print(f"已自动汇集退休呈报表数据: 教师ID={teacher_id}, 姓名={teacher_row[1]}")
            except Exception as e:
                error_msg = f"自动汇集退休呈报表数据失败: {str(e)}"
                print(error_msg)
                import traceback
                traceback.print_exc()
                data_collection_error = error_msg
                # 不影响主流程，继续执行
        
        # 根据目标状态查找匹配的清单模板并创建待办
        created_checklists = []
        
        # 查找所有有效的清单模板
        cursor.execute("""
            SELECT id, "清单名称", "任务项列表", "触发条件", "关联模板ID"
            FROM business_checklist
            WHERE "是否有效" = true
        """)
        
        all_checklists = cursor.fetchall()
        print(f"找到 {len(all_checklists)} 个有效清单模板")
        print(f"目标状态: {target_status}")
        
        # 筛选匹配的清单
        matched_checklists = []
        for checklist_row in all_checklists:
            checklist_id = checklist_row[0]
            checklist_name = checklist_row[1]
            task_items = checklist_row[2] if isinstance(checklist_row[2], list) else json.loads(checklist_row[2]) if checklist_row[2] else []
            trigger_condition = checklist_row[3] if isinstance(checklist_row[3], dict) else json.loads(checklist_row[3]) if checklist_row[3] else {}
            associated_template_id = checklist_row[4]  # 关联模板ID
            
            print(f"检查清单: {checklist_name}, 触发条件: {trigger_condition}, 关联模板: {associated_template_id}")
            
            # 检查触发条件是否匹配当前状态
            target_statuses = trigger_condition.get("target_status", [])
            print(f"  target_statuses: {target_statuses}, 类型: {type(target_statuses)}")
            
            if isinstance(target_statuses, str):
                target_statuses = [target_statuses]
            
            # 如果当前状态在触发列表中，添加到匹配列表
            print(f"  检查 {target_status} 是否在 {target_statuses}: {target_status in target_statuses}")
            if target_status in target_statuses:
                matched_checklists.append({
                    "id": checklist_id,
                    "name": checklist_name,
                    "task_items": task_items,
                    "associated_template_id": associated_template_id
                })
        
        # 如果没有匹配的清单，返回提示信息
        if not matched_checklists:
            conn.commit()
            cursor.close()
            conn.close()
            
            return {
                "status": "no_checklist",
                "message": f"当前任职状态 '{target_status}' 下没有待办任务清单",
                "teacher_id": teacher_id,
                "new_status": target_status,
                "created_checklists": []
            }
        
        # 创建待办工作
        for checklist in matched_checklists:
            checklist_id = checklist["id"]
            checklist_name = checklist["name"]
            task_items = checklist["task_items"]
            associated_template_id = checklist["associated_template_id"]
            
            # 检查是否已存在该待办
            cursor.execute("""
                SELECT id FROM todo_work
                WHERE 教师ID = %s AND 清单ID = %s AND 状态 = 'pending'
            """, (teacher_id, checklist_id))
            
            if not cursor.fetchone():
                # 判断模板类型（检查是否是通用模板）
                template_type = 'old'
                if associated_template_id:
                    cursor.execute("""
                        SELECT 1 FROM universal_templates WHERE template_id = %s
                    """, (associated_template_id,))
                    if cursor.fetchone():
                        template_type = 'universal'
                        print(f"【状态变更】检测到通用模板: {associated_template_id}")
                
                # 处理任务项，添加关联模板ID到任务参数
                processed_task_items = []
                for task in task_items:
                    processed_task = task.copy()
                    if '参数' not in processed_task:
                        processed_task['参数'] = {}
                    # 如果清单模板有关联模板ID，且任务没有指定模板ID，则使用清单的模板ID
                    if associated_template_id and not processed_task['参数'].get('template_id'):
                        processed_task['参数']['template_id'] = associated_template_id
                        processed_task['参数']['template_type'] = template_type
                    processed_task_items.append(processed_task)
                
                # 创建待办工作
                total_tasks = len(processed_task_items)
                cursor.execute("""
                    INSERT INTO todo_work 
                    (教师ID, 清单ID, 清单名称, 教师姓名, 任务项列表, 总任务数, 已完成数, 状态)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    teacher_id,
                    checklist_id,
                    checklist_name,
                    teacher_name,
                    json.dumps(processed_task_items),
                    total_tasks,
                    0,
                    "pending"
                ))
                
                todo_id = cursor.fetchone()[0]
                created_checklists.append({
                    "todo_id": todo_id,
                    "checklist_name": checklist_name,
                    "total_tasks": total_tasks
                })
        
        conn.commit()
        cursor.close()
        conn.close()
        
        # 构建响应
        response_data = {
            "status": "success",
            "message": f"状态变更处理成功",
            "teacher_id": teacher_id,
            "new_status": target_status,
            "created_checklists": created_checklists
        }
        
        # 如果数据汇集有错误，添加警告信息
        if data_collection_error:
            response_data["status"] = "warning"
            response_data["message"] = f"状态更新成功，但数据汇集失败: {data_collection_error}"
            response_data["data_collection_error"] = data_collection_error
        
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"处理状态变更失败: {e}")
        raise HTTPException(status_code=500, detail=f"处理状态变更失败: {str(e)}")
