"""
状态变更处理路由
当教师任职状态变更时，自动匹配业务清单模板并创建待办工作项
"""
from fastapi import APIRouter, HTTPException
from typing import Any
import psycopg2
import json
import logging
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.dict_utils import get_education_name

logger = logging.getLogger(__name__)

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


def _build_retirement_report_data(cursor, teacher_id, teacher_row, id_card, education_row):
    """构建退休呈报表完整数据 - 从多个数据源自动汇集
    
    数据源：
    1. teacher_basic_info - 基础信息、出生日期
    2. post_appointment_info - 职务、职称
    3. salary_data - 三个时间点的职务岗位和级别薪级
    4. retirement_info - 退休补充信息
    """
    from datetime import datetime as dt
    
    # ==================== 一、基础信息处理 ====================
    # 出生日期：优先档案出生日期，否则出生日期
    birth_date = teacher_row[3]  # 档案出生日期
    if not birth_date:
        # 尝试从 teacher_basic_info 获取出生日期字段
        cursor.execute('SELECT "出生日期" FROM teacher_basic_info WHERE id = %s', (teacher_id,))
        bd_row = cursor.fetchone()
        if bd_row and bd_row[0]:
            birth_date = str(bd_row[0])
    if not birth_date and id_card and len(id_card) == 18:
        try:
            birth_date = f"{id_card[6:10]}-{id_card[10:12]}-{id_card[12:14]}"
        except:
            pass
    
    # 性别从身份证提取
    gender = None
    if id_card and len(id_card) == 18:
        try:
            gender = "男" if int(id_card[16]) % 2 == 1 else "女"
        except:
            pass
    
    # 工作年限
    work_years = 0
    if teacher_row[6]:
        try:
            start = dt.strptime(str(teacher_row[6]), "%Y-%m-%d")
            today = dt.now()
            work_years = today.year - start.year
            if (today.month, today.day) < (start.month, start.day):
                work_years -= 1
        except:
            pass
    
    education_name = get_education_name(education_row[0], DATABASE_CONFIG) if education_row else None
    
    # ==================== 二、职务和职称（岗位聘任信息） ====================
    # 职务等级映射：post_level_1 -> 正高级/副高级/中级/初级
    POST_LEVEL_TO_TITLE = {
        4: '正高级',    # 四级专技
        5: '副高级',    # 五级专技
        6: '副高级',    # 六级专技
        7: '副高级',    # 七级专技
        8: '中级',      # 八级专技
        9: '中级',      # 九级专技
        10: '中级',     # 十级专技
        11: '初级',     # 11级专技
        12: '初级',     # 12级专技
        2: '初级',      # 二级
        3: '初级',      # 三级
        15: '副高级',   # 15级
        17: '正高级',   # 17级
    }
    
    position_title = None  # 职务（正高级/副高级/中级/初级）
    professional_title = None  # 职称（高级教师/一级教师等）
    duty = None  # 岗位
    
    cursor.execute("""
        SELECT post_level_1, professional_title, duty, job_title
        FROM post_appointment_info
        WHERE id_card = %s
        ORDER BY id DESC LIMIT 1
    """, (id_card,))
    post_row = cursor.fetchone()
    if post_row:
        if post_row[0] is not None:
            try:
                level = int(post_row[0])
                position_title = POST_LEVEL_TO_TITLE.get(level)
            except (ValueError, TypeError):
                pass
        professional_title = post_row[1]
        duty = post_row[2]
    
    # ==================== 三、单位岗位区（最新工资包数据） ====================
    # 确定人员分类
    # 机关工人、事业管理（职务岗位包含管理）、事业专技（包含专技或义教）、事业工勤（包含技工）
    salary_time_points = {
        '2014年9月30日': {'job_title': None, 'salary_level': None, 'salary': None, 'position_salary': None},
        '最后一次职务升降时间': {'time': None, 'job_title': None, 'salary_level': None, 'salary': None, 'position_salary': None},
        '退休时': {'job_title': None, 'salary_level': None, 'salary': None, 'position_salary': None},
    }
    
    # 查询该教师的所有工资记录
    cursor.execute("""
        SELECT job_title_post, field_21, time, salary, salary_1, type, type_1
        FROM salary_data
        WHERE id_card_1 = %s
        ORDER BY time
    """, (id_card,))
    salary_rows = cursor.fetchall()
    
    if salary_rows:
        # 1) 2014年9月30日：起薪时间=2014-10-01
        for row in salary_rows:
            if row[2] and str(row[2]) == '2014-10-01':
                salary_time_points['2014年9月30日']['job_title'] = row[0]
                salary_time_points['2014年9月30日']['salary_level'] = row[1]
                salary_time_points['2014年9月30日']['salary'] = row[3]
                salary_time_points['2014年9月30日']['position_salary'] = row[4]
                break
        
        # 2) 最后一次职务升降时间：职务岗位最高一级对应的最小起薪时间
        # 职务岗位从高到低：四级->五级->...->13级
        # 解析职务岗位等级
        def parse_job_rank(job_title):
            """解析职务岗位等级，返回数字以便比较（数字越小，级别越高）"""
            if not job_title:
                return 999
            import re
            # 匹配中文数字或阿拉伯数字
            chinese_map = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9, '十': 10}
            for ch, num in chinese_map.items():
                if ch in str(job_title):
                    return num
            # 匹配阿拉伯数字
            match = re.search(r'(\d+)', str(job_title))
            if match:
                return int(match.group(1))
            return 999
        
        # 找出最高职务岗位等级（数字最小）
        best_rank = 999
        best_row = None
        for row in salary_rows:
            rank = parse_job_rank(row[0])
            if rank < best_rank:
                best_rank = rank
                best_row = row
        
        if best_row:
            salary_time_points['最后一次职务升降时间']['time'] = best_row[2]
            salary_time_points['最后一次职务升降时间']['job_title'] = best_row[0]
            salary_time_points['最后一次职务升降时间']['salary_level'] = best_row[1]
            salary_time_points['最后一次职务升降时间']['salary'] = best_row[3]
            salary_time_points['最后一次职务升降时间']['position_salary'] = best_row[4]
        
        # 3) 退休时：最大起薪时间
        max_time_row = max(salary_rows, key=lambda r: r[2] if r[2] else '')
        salary_time_points['退休时']['job_title'] = max_time_row[0]
        salary_time_points['退休时']['salary_level'] = max_time_row[1]
        salary_time_points['退休时']['salary'] = max_time_row[3]
        salary_time_points['退休时']['position_salary'] = max_time_row[4]
    
    # ==================== 四、退休补充信息 ====================
    retirement_info = {}
    cursor.execute("""
        SELECT children, name_birth_date
        FROM retirement_info
        WHERE id_card = %s ORDER BY id DESC LIMIT 1
    """, (id_card,))
    ri_row = cursor.fetchone()
    if ri_row:
        retirement_info['是否独生子女'] = ri_row[0]
        retirement_info['供养亲属'] = ri_row[1]
    
    # ==================== 五、构建返回数据 ====================
    return {
        # 基础信息
        "姓名": teacher_row[1],
        "身份证号码": id_card,
        "性别": gender,
        "出生日期": birth_date,
        "民族": teacher_row[4],
        "文化程度": education_name,
        "参加工作时间": teacher_row[6],
        "工作年限": work_years,
        "籍贯": teacher_row[5],
        # 职务职称
        "职务": position_title,
        "技术职称": professional_title,
        "岗位": duty,
        # 单位岗位区 - 三个时间点
        "2014年9月30日职务岗位": salary_time_points['2014年9月30日']['job_title'],
        "2014年9月30日级别薪级": salary_time_points['2014年9月30日']['salary_level'],
        "2014年9月30日薪级工资": salary_time_points['2014年9月30日']['salary'],
        "2014年9月30日岗位工资": salary_time_points['2014年9月30日']['position_salary'],
        "最后一次职务升降时间": salary_time_points['最后一次职务升降时间']['time'],
        "最后一次职务升降岗位": salary_time_points['最后一次职务升降时间']['job_title'],
        "最后一次职务升降薪级": salary_time_points['最后一次职务升降时间']['salary_level'],
        "最后一次职务升降薪级工资": salary_time_points['最后一次职务升降时间']['salary'],
        "最后一次职务升降岗位工资": salary_time_points['最后一次职务升降时间']['position_salary'],
        "退休时职务岗位": salary_time_points['退休时']['job_title'],
        "退休时级别薪级": salary_time_points['退休时']['salary_level'],
        "退休时薪级工资": salary_time_points['退休时']['salary'],
        "退休时岗位工资": salary_time_points['退休时']['position_salary'],
        # 退休补充信息
        "退休原因": None,  # retirement_info 表中暂无此字段
        "是否独生子女": retirement_info.get('是否独生子女'),
        "供养亲属": retirement_info.get('供养亲属'),
        "现住址": None,  # retirement_info 表中暂无此字段
        "退休后居住地址": None,  # retirement_info 表中暂无此字段
        "发给退休费的单位": None,  # retirement_info 表中暂无此字段
        "工作经历": None,  # retirement_info 表中暂无此字段
        "单位意见": None,
        "证明人及其住址": None,
        "直系亲属信息": None,
        "入党年月": None,
        "退休时间": None,
    }


def _write_remark(teacher_id, teacher_name, old_status, target_status):
    """写入任职状态变更备注"""
    remark_conn = None
    remark_cursor = None
    try:
        remark_conn = get_db_connection()
        remark_cursor = remark_conn.cursor()

        id_card = None
        remark_cursor.execute(
            'SELECT "身份证号码" FROM teacher_basic_info WHERE id = %s', (teacher_id,))
        id_card_row = remark_cursor.fetchone()
        if id_card_row:
            id_card = id_card_row[0]

        original_post = None
        if id_card:
            remark_cursor.execute("SELECT id, post FROM dict_dictionary_personal")
            dict_mapping = {}
            for dict_row in remark_cursor.fetchall():
                dict_mapping[dict_row[0]] = dict_row[1]

            remark_cursor.execute(
                "SELECT post_1 FROM post_appointment_info WHERE id_card = %s", (id_card,))
            post_row = remark_cursor.fetchone()
            if post_row and post_row[0]:
                post_id = int(post_row[0])
                original_post = dict_mapping.get(post_id, f'未知岗位{post_id}')

        current_month = datetime.now().strftime('%Y-%m')
        remark_cursor.execute("""
            INSERT INTO performance_pay_remarks (
                report_period, remark_type, teacher_id, teacher_name,
                original_status, new_status, original_post, new_post,
                change_category, change_detail, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
        """, (
            current_month, 'status_change', teacher_id, teacher_name,
            old_status, target_status, original_post, None,
            'status_change', f'{old_status}->{target_status}'
        ))
        remark_conn.commit()
        logger.info(f"已写入任职状态变更备注: {teacher_name} {old_status}->{target_status}")
    except Exception as e:
        logger.error(f"写入备注信息失败: {e}")
        if remark_conn:
            try:
                remark_conn.rollback()
            except:
                pass
    finally:
        if remark_cursor:
            remark_cursor.close()
        if remark_conn:
            remark_conn.close()


@router.post("/process")
async def process_status_change(data: dict[str, Any]):
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
            SELECT "任职状态", "姓名" FROM teacher_basic_info WHERE id = %s
        """, (teacher_id,))
        row = cursor.fetchone()
        old_status = row[0] if row else None
        teacher_name = data.get("teacher_name") or (row[1] if row else "未知")
        
        # 更新教师状态
        cursor.execute("""
            UPDATE teacher_basic_info 
            SET "任职状态" = %s
            WHERE id = %s
        """, (target_status, teacher_id))

        conn.commit()

        # 自动写入备注信息表
        if old_status and old_status != target_status:
            _write_remark(teacher_id, teacher_name, old_status, target_status)

        # 实时触发提醒已经在下面的循环中处理了
        # 后续主流程会正确匹配并创建待办，这里不需要重复处理
        
        # 如果状态变更为退休，自动汇集退休呈报表数据
        data_collection_error = None
        if target_status == '退休':
            try:
                cursor.execute("""
                    SELECT id, "姓名", "身份证号码", "档案出生日期", "民族", 
                           "籍贯", "参加工作日期",
                           "任职状态", "联系电话"
                    FROM teacher_basic_info 
                    WHERE id = %s
                """, (teacher_id,))
                
                teacher_row = cursor.fetchone()
                if teacher_row:
                    id_card = teacher_row[2]
                    
                    # 查询最高学历信息
                    cursor.execute("""
                        SELECT education, graduate_date, graduate_school, major
                        FROM teacher_education_record
                        WHERE teacher_id = %s
                        ORDER BY graduate_date DESC
                        LIMIT 1
                    """, (teacher_id,))
                    education_row = cursor.fetchone()
                    
                    # 使用辅助函数构建完整数据
                    report_data = _build_retirement_report_data(cursor, teacher_id, teacher_row, id_card, education_row)
                    
                    # 检查是否已存在该教师的记录
                    cursor.execute("""
                        SELECT id FROM retirement_report_data WHERE teacher_id = %s
                    """, (teacher_id,))
                    existing_row = cursor.fetchone()
                    
                    if existing_row:
                        cursor.execute("""
                            UPDATE retirement_report_data SET
                                姓名 = %s, 身份证号码 = %s, 性别 = %s, 出生日期 = %s,
                                民族 = %s, 文化程度 = %s, 参加工作时间 = %s, 工作年限 = %s,
                                籍贯 = %s,
                                现住址 = %s,
                                职务 = %s, 岗位 = %s, 技术职称 = %s,
                                退休原因 = %s, 退休后居住地址 = %s, 退休时间 = %s,
                                单位意见 = %s, 证明人及其住址 = %s, 直系亲属信息 = %s,
                                是否独生子女 = %s, 入党年月 = %s,
                                薪级工资 = %s, 岗位工资 = %s, 技术等级 = %s,
                                最后一次职务升降时间 = %s,
                                薪级1 = %s, 薪级2 = %s, 薪级3 = %s,
                                对应原职务1 = %s, 对应原职务2 = %s, 对应原职务3 = %s,
                                updated_at = NOW()
                            WHERE teacher_id = %s
                        """, (
                            report_data['姓名'], report_data['身份证号码'], report_data['性别'], report_data['出生日期'],
                            report_data['民族'], report_data['文化程度'], report_data['参加工作时间'], report_data['工作年限'],
                            report_data['籍贯'],
                            report_data['现住址'],
                            report_data['职务'], report_data['岗位'], report_data['技术职称'],
                            report_data['退休原因'], report_data['退休后居住地址'], report_data['退休时间'],
                            report_data['单位意见'], report_data['证明人及其住址'], report_data['直系亲属信息'],
                            report_data['是否独生子女'], report_data['入党年月'],
                            report_data['退休时薪级工资'], report_data['退休时岗位工资'], None,
                            report_data['最后一次职务升降时间'],
                            # 薪级1-3：2014年、最后一次、退休时
                            report_data['2014年9月30日级别薪级'],
                            report_data['最后一次职务升降薪级'],
                            report_data['退休时级别薪级'],
                            # 对应原职务1-3
                            report_data['2014年9月30日职务岗位'],
                            report_data['最后一次职务升降岗位'],
                            report_data['退休时职务岗位'],
                            teacher_id
                        ))
                    else:
                        cursor.execute("""
                            INSERT INTO retirement_report_data (
                                teacher_id, 姓名, 身份证号码, 性别, 出生日期, 
                                民族, 文化程度, 参加工作时间, 工作年限,
                                籍贯, 现住址, 职务, 岗位, 技术职称,
                                退休原因, 退休后居住地址, 退休时间, 单位意见,
                                证明人及其住址, 直系亲属信息, 是否独生子女,
                                入党年月, 薪级工资, 岗位工资, 技术等级,
                                最后一次职务升降时间,
                                薪级1, 薪级2, 薪级3,
                                对应原职务1, 对应原职务2, 对应原职务3,
                                created_at, updated_at
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                        """, (
                            teacher_id,
                            report_data['姓名'], report_data['身份证号码'], report_data['性别'], report_data['出生日期'],
                            report_data['民族'], report_data['文化程度'], report_data['参加工作时间'], report_data['工作年限'],
                            report_data['籍贯'],
                            report_data['现住址'],
                            report_data['职务'], report_data['岗位'], report_data['技术职称'],
                            report_data['退休原因'], report_data['退休后居住地址'], report_data['退休时间'],
                            report_data['单位意见'], report_data['证明人及其住址'], report_data['直系亲属信息'],
                            report_data['是否独生子女'], report_data['入党年月'],
                            report_data['退休时薪级工资'], report_data['退休时岗位工资'], None,
                            report_data['最后一次职务升降时间'],
                            report_data['2014年9月30日级别薪级'],
                            report_data['最后一次职务升降薪级'],
                            report_data['退休时级别薪级'],
                            report_data['2014年9月30日职务岗位'],
                            report_data['最后一次职务升降岗位'],
                            report_data['退休时职务岗位'],
                        ))
                    
                    logger.info(f"已自动汇集退休呈报表数据: 教师ID={teacher_id}, 姓名={teacher_row[1]}")
            except Exception as e:
                error_msg = f"自动汇集退休呈报表数据失败: {str(e)}"
                logger.error(error_msg)
                import traceback
                traceback.print_exc()
                data_collection_error = error_msg
                try:
                    conn.rollback()
                except:
                    pass
                try:
                    conn.commit()
                except:
                    pass
        
        # 根据目标状态查找匹配的清单模板并创建待办
        created_checklists = []
        
        # 查找所有有效的清单模板
        cursor.execute("""
            SELECT id, "清单名称", "任务项列表", "触发条件", "关联模板ID"
            FROM business_checklist
            WHERE "是否有效" = true
        """)
        
        all_checklists = cursor.fetchall()
        logger.info(f"找到 {len(all_checklists)} 个有效清单模板, 目标状态: {target_status}")
        
        # 筛选匹配的清单
        matched_checklists = []
        for checklist_row in all_checklists:
            checklist_id = checklist_row[0]
            checklist_name = checklist_row[1]
            
            # 安全解析JSON字段，避免事务abort
            try:
                task_items = checklist_row[2] if isinstance(checklist_row[2], (dict, list)) else json.loads(checklist_row[2]) if checklist_row[2] else []
            except (json.JSONDecodeError, TypeError) as e:
                logger.warning(f"解析task_items失败: {e}, 使用空列表")
                task_items = []
            
            try:
                trigger_condition = checklist_row[3] if isinstance(checklist_row[3], dict) else (checklist_row[3] if isinstance(checklist_row[3], list) else json.loads(checklist_row[3]) if checklist_row[3] else {})
            except (json.JSONDecodeError, TypeError) as e:
                logger.warning(f"解析trigger_condition失败: {e}, 使用空字典")
                trigger_condition = {}
            
            associated_template_id = checklist_row[4]  # 关联模板ID
            
            logger.debug(f"检查清单: {checklist_name}, 触发条件: {trigger_condition}, 关联模板: {associated_template_id}")
            
            # 检查触发条件是否匹配当前状态
            target_statuses = trigger_condition.get("target_status", []) if isinstance(trigger_condition, dict) else []
            logger.debug(f"  target_statuses: {target_statuses}, 类型: {type(target_statuses)}")
            
            if isinstance(target_statuses, str):
                target_statuses = [target_statuses]
            
            # 如果当前状态在触发列表中，添加到匹配列表
            logger.debug(f"  检查 {target_status} 是否在 {target_statuses}: {target_status in target_statuses}")
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
            
            # 检查是否已存在该待办（使用 todo_items 表）
            cursor.execute("""
                SELECT id FROM todo_items
                WHERE teacher_id = %s AND template_id = %s AND status = 'pending'
        """, (teacher_id, str(checklist_id)))
            
            if not cursor.fetchone():
                # 判断模板类型（检查是否是通用模板）
                template_type = 'old'
                if associated_template_id:
                    cursor.execute("""
                        SELECT 1 FROM universal_templates WHERE template_id = %s
                    """, (associated_template_id,))
                    if cursor.fetchone():
                        template_type = 'universal'
                        logger.info(f"【状态变更】检测到通用模板: {associated_template_id}")
                
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
                
                # 创建待办工作（使用 todo_items 表）
                total_tasks = len(processed_task_items)
                cursor.execute("""
                    INSERT INTO todo_items 
                    (teacher_id, template_id, business_type, teacher_name, title, description, task_items, status, created_by)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    teacher_id,
                    checklist_id,
                    'RETIREMENT',
                    teacher_name,
                    f"{teacher_name}{checklist_name}",
                    f"状态变更触发: {target_status}",
                    json.dumps(processed_task_items),
                    "pending",
                    "system"
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
        logger.error(f"处理状态变更失败: {e}")
        raise HTTPException(status_code=500, detail=f"处理状态变更失败: {str(e)}")
