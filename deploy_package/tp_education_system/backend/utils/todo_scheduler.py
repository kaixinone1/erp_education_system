#!/usr/bin/env python3
"""
待办任务定时调度器
- 每天凌晨2:00自动扫描推送80周岁高龄补贴待办
- 每天凌晨2:00自动扫描推送到龄退休提醒待办
"""
import psycopg2
import json
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

DATABASE_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "database": "taiping_education",
    "user": "taiping_user",
    "password": "taiping_password"
}

def get_db_connection():
    """获取数据库连接"""
    return psycopg2.connect(**DATABASE_CONFIG)

def get_birth_date_from_id_card(id_card):
    """从身份证号解析出生日期"""
    if not id_card or len(id_card) != 18:
        return None
    try:
        year = int(id_card[6:10])
        month = int(id_card[10:12])
        day = int(id_card[12:14])
        return datetime(year, month, day).date()
    except:
        return None

def get_80th_birthday(birth_date):
    """计算80周岁生日日期"""
    if not birth_date:
        return None
    return birth_date + relativedelta(years=80)

def get_retirement_date(birth_date, gender):
    """
    计算退休年龄日期（旧政策）
    - 男：60周岁
    - 女：55周岁
    """
    if not birth_date:
        return None
    
    if gender and '女' in str(gender):
        retirement_age = 55
    else:
        retirement_age = 60
    
    return birth_date + relativedelta(years=retirement_age)


def calculate_retirement_new_policy(birth_date, gender, is_cadre=False):
    """
    按新退休政策计算退休日期
    
    参数:
    - birth_date: 出生日期
    - gender: 性别（男/女）
    - is_cadre: 是否干部（是/否）
    
    返回:
    - 原退休日期, 延迟月数, 新退休日期
    """
    if not birth_date:
        return None, 0, None
    
    # 1. 计算原退休日期
    if gender == '男':
        original_retirement_age = 60
    elif is_cadre:
        original_retirement_age = 55  # 女干部
    else:
        original_retirement_age = 50  # 女工人
    
    original_retirement_date = birth_date + relativedelta(years=original_retirement_age)
    
    # 2. 计算延迟月数
    delay_months = 0
    
    if gender == '男':
        # 男性：出生日期 < 1976-09-01
        if birth_date < datetime(1976, 9, 1).date():
            # 计算从2025-01-01到原退休日期的月数
            months_diff = (original_retirement_date.year - 2025) * 12 + (original_retirement_date.month - 1)
            delay_months = min(int(months_diff / 4 + 1), 36)
        else:
            delay_months = 36
    elif gender == '女':
        if is_cadre:
            # 女性干部：出生日期 < 1981-09-01
            if birth_date < datetime(1981, 9, 1).date():
                months_diff = (original_retirement_date.year - 2025) * 12 + (original_retirement_date.month - 1)
                delay_months = min(int(months_diff / 4 + 1), 36)
            else:
                delay_months = 36
        else:
            # 女性非干部：出生日期 < 1984-11-01
            if birth_date < datetime(1984, 11, 1).date():
                months_diff = (original_retirement_date.year - 2025) * 12 + (original_retirement_date.month - 1)
                delay_months = min(int(months_diff / 2 + 1), 60)
            else:
                delay_months = 60
    
    # 3. 计算新退休日期
    new_retirement_date = original_retirement_date + relativedelta(months=delay_months)
    
    return original_retirement_date, delay_months, new_retirement_date

def get_gender_from_id_card(id_card):
    """从身份证号获取性别"""
    if not id_card or len(id_card) != 18:
        return None
    try:
        gender_code = int(id_card[16])
        return '女' if gender_code % 2 == 0 else '男'
    except:
        return None

def scan_octogenarian_subsidy():
    """
    扫描80周岁高龄补贴待办
    提前60天推送提醒
    """
    logger.info("[开始] 扫描80周岁高龄补贴待办")
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        today = datetime.now().date()
        advance_days = 60
        
        # 1. 查询已导入的高龄老人补贴信息表中的身份证号码
        cursor.execute('SELECT 身份证号码 FROM "高龄老人补贴信息" WHERE 状态 != %s', ('死亡',))
        existing_ids = set(row[0] for row in cursor.fetchall())
        logger.info(f"  已导入的高龄补贴人数: {len(existing_ids)}")
        
        # 2. 查询所有教师（只要有身份证号即可）
        cursor.execute("""
            SELECT 
                id,
                name,
                id_card,
                archive_birth_date
            FROM teacher_basic_info
            WHERE id_card IS NOT NULL
              AND id_card != ''
            ORDER BY id
        """)
        
        teachers = cursor.fetchall()
        logger.info(f"  教师基础信息表总人数: {len(teachers)}")
        
        # 3. 筛选符合条件的教师
        eligible_teachers = []
        for teacher in teachers:
            teacher_id, name, id_card, birth_date = teacher
            
            # 优先使用数据库中的出生日期，如果没有则从身份证号解析
            if not birth_date:
                birth_date = get_birth_date_from_id_card(id_card)
            
            if not birth_date:
                continue
                
            birthday_80 = get_80th_birthday(birth_date)
            if not birthday_80:
                continue
            
            days_until_80 = (birthday_80 - today).days
            
            # 从2026年1月1日起开始推送
            if birthday_80.year >= 2026 and 0 <= days_until_80 <= advance_days:
                if id_card not in existing_ids:
                    eligible_teachers.append({
                        'teacher_id': teacher_id,
                        'name': name,
                        'id_card': id_card,
                        'birthday_80': birthday_80,
                        'days_until': days_until_80
                    })
        
        logger.info(f"  符合条件的人数: {len(eligible_teachers)}")
        
        if len(eligible_teachers) == 0:
            logger.info("[完成] 没有需要推送的80周岁高龄补贴待办")
            return
        
        # 4. 使用用户设计好的模板 OCTOGENARIAN_001
        template_code = 'OCTOGENARIAN_001'
        logger.info(f"  使用模板: {template_code}")
        
        # 从模板获取任务项
        cursor.execute("SELECT task_flow FROM todo_templates WHERE template_code = %s", (template_code,))
        template_row = cursor.fetchone()
        template_task_items = template_row[0] if template_row else None
        if template_task_items and isinstance(template_task_items, str):
            template_task_items = json.loads(template_task_items)
        
        # 5. 创建待办事项
        created_count = 0
        for teacher in eligible_teachers:
            # 检查是否已存在待办（不管状态如何，只要存在就不创建）
            cursor.execute("""
                SELECT id FROM todo_items 
                WHERE teacher_id = %s 
                  AND template_id = %s
            """, (teacher['teacher_id'], str(template_code)))
            
            if cursor.fetchone():
                continue
            
            # 检查历史记录中是否已有过该教师的退休提醒（不管是否完成）
            cursor.execute("""
                SELECT id FROM todo_history 
                WHERE teacher_id = %s 
                  AND (business_type LIKE %s OR business_type LIKE %s OR business_type = %s)
            """, (teacher['teacher_id'], '%retirement%', '%退休%', 'RETIREMENT_REMIND'))
            
            if cursor.fetchone():
                logger.info(f"    [跳过] {teacher['name']} - 历史记录中已有退休提醒")
                continue
            
            # 使用模板的任务项
            task_items = template_task_items if template_task_items else []
            
            # 插入待办
            cursor.execute("""
                INSERT INTO todo_items (
                    template_id,
                    business_type,
                    teacher_id,
                    teacher_name,
                    title,
                    description,
                    due_date,
                    status,
                    priority,
                    task_items,
                    created_at,
                    updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
            """, (
                template_code,
                'octogenarian_subsidy',
                teacher['teacher_id'],
                teacher['name'],
                f"{teacher['name']} - 80周岁高龄补贴申请",
                f"教师 {teacher['name']} 将于 {teacher['birthday_80'].strftime('%Y年%m月%d日')} 年满80周岁，"
                f"距离现在还有 {teacher['days_until']} 天，请提前办理高龄补贴申请。",
                teacher['birthday_80'],
                'pending',
                'high' if teacher['days_until'] <= 30 else 'normal',
                json.dumps(task_items)
            ))
            
            created_count += 1
            
            # 创建待办历史记录
            cursor.execute("""
                INSERT INTO todo_history (
                    todo_id, teacher_id, teacher_name, template_code, business_type,
                    title, description, status, task_items, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
            """, (
                cursor.lastrowid, teacher['teacher_id'], teacher['name'], template_code,
                'octogenarian_subsidy',
                f"{teacher['name']} - 80周岁高龄补贴申请",
                f"教师 {teacher['name']} 将于 {teacher['birthday_80'].strftime('%Y年%m月%d日')} 年满80周岁，距离现在还有 {teacher['days_until']} 天",
                'pending',
                json.dumps(task_items)
            ))
            
            logger.info(f"    [创建] {teacher['name']} - 80周岁日期: {teacher['birthday_80']}, 还剩{teacher['days_until']}天")
        
        conn.commit()
        logger.info(f"[完成] 新建80周岁高龄补贴待办: {created_count}")
        
    except Exception as e:
        conn.rollback()
        logger.error(f"[错误] 扫描80周岁高龄补贴待办失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cursor.close()
        conn.close()

def scan_retirement_reminder():
    """
    扫描到龄退休提醒待办
    提前7周（49天）推送提醒
    """
    logger.info("[开始] 扫描到龄退休提醒待办")
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        today = datetime.now().date()
        advance_days = 49  # 7周
        
        # 1. 查询任职状态字典，找到"退休"状态的值
        cursor.execute("""
            SELECT employment_status FROM dict_dictionary 
            WHERE employment_status = %s OR status_code = %s
            LIMIT 1
        """, ('退休', '退休'))
        
        result = cursor.fetchone()
        retired_status = result[0] if result else '退休'
        
        # 排除的任职状态列表
        excluded_statuses = ['退休', '离休', '死亡', '去世', '调离', '离职']
        
        # 2. 查询教师基础信息表，排除已退休/离休/死亡/调离/离职等状态的教师
        cursor.execute("""
            SELECT 
                t.id,
                t.name,
                t.id_card,
                t.archive_birth_date,
                t.employment_status,
                t.is_cadre,
                u.unit_1 as unit_name,
                p.ge_ren_shen_fen as personal_identity
            FROM teacher_basic_info t
            LEFT JOIN teacher_unit u ON t.id_card = u.id_card
            LEFT JOIN teacher_personal_identity p ON t.id_card = p.id_card
            WHERE t.id_card IS NOT NULL
              AND t.id_card != ''
              AND (t.employment_status IS NULL OR t.employment_status NOT IN %s)
            ORDER BY t.id
        """, (tuple(excluded_statuses),))
        
        teachers = cursor.fetchall()
        logger.info(f"  未退休教师人数: {len(teachers)}")
        
        # 3. 筛选符合条件的教师
        eligible_teachers = []
        for teacher in teachers:
            teacher_id, name, id_card, birth_date, work_status, is_cadre, unit_name, personal_identity = teacher
            
            # 优先使用数据库中的出生日期，如果没有则从身份证号解析
            if not birth_date:
                birth_date = get_birth_date_from_id_card(id_card)
            
            if not birth_date:
                continue
            
            gender = get_gender_from_id_card(id_card)
            if not gender:
                gender = '男'
            
            # 使用新政策计算退休日期
            original_date, delay_months, retirement_date = calculate_retirement_new_policy(
                birth_date, gender, personal_identity == '是' or is_cadre == '是'
            )
            if not retirement_date:
                continue
            
            days_until_retirement = (retirement_date - today).days
            
            # 从2026年1月1日起开始推送
            if retirement_date.year >= 2026 and 0 <= days_until_retirement <= advance_days:
                eligible_teachers.append({
                    'teacher_id': teacher_id,
                    'name': name,
                    'id_card': id_card,
                    'gender': gender,
                    'retirement_date': retirement_date,
                    'days_until': days_until_retirement,
                    'retirement_age': 55 if gender == '女' else 60
                })
        
        logger.info(f"  符合条件的人数: {len(eligible_teachers)}")
        
        if len(eligible_teachers) == 0:
            logger.info("[完成] 没有需要推送的到龄退休提醒待办")
            return
        
        # 4. 使用用户设计好的模板 RETIREMENT_REMIND
        template_code = 'RETIREMENT_REMIND'
        logger.info(f"  使用模板: {template_code}")
        
        # 从模板获取任务项
        cursor.execute("SELECT task_flow FROM todo_templates WHERE template_code = %s", (template_code,))
        template_row = cursor.fetchone()
        template_task_items = template_row[0] if template_row else None
        if template_task_items and isinstance(template_task_items, str):
            template_task_items = json.loads(template_task_items)
        
        # 5. 创建待办事项
        created_count = 0
        for teacher in eligible_teachers:
            # 检查是否已存在待办（不管状态如何，只要存在就不创建）
            cursor.execute("""
                SELECT id FROM todo_items 
                WHERE teacher_id = %s 
                  AND template_id = %s
            """, (teacher['teacher_id'], str(template_code)))
            
            if cursor.fetchone():
                continue
            
            # 使用模板的任务项
            task_items = template_task_items if template_task_items else []
            
            cursor.execute("""
                INSERT INTO todo_items (
                    template_id,
                    business_type,
                    teacher_id,
                    teacher_name,
                    title,
                    description,
                    due_date,
                    status,
                    priority,
                    task_items,
                    created_at,
                    updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
            """, (
                template_code,
                'retirement_reminder',
                teacher['teacher_id'],
                teacher['name'],
                f"{teacher['name']} - 到龄退休审批（{teacher['retirement_age']}岁）",
                f"教师 {teacher['name']}（{teacher['gender']}）将于 {teacher['retirement_date'].strftime('%Y年%m月%d日')} "
                f"年满{teacher['retirement_age']}周岁，"
                f"距离现在还有 {teacher['days_until']} 天，请提前办理退休审批手续。",
                teacher['retirement_date'],
                'pending',
                'high' if teacher['days_until'] <= 14 else 'normal',
                json.dumps(task_items)
            ))
            
            created_count += 1
            
            # 获取刚创建的待办ID
            cursor.execute("SELECT lastval()")
            new_todo_id = cursor.fetchone()[0]
            
            # 创建待办历史记录
            cursor.execute("""
                INSERT INTO todo_history (
                    todo_id, teacher_id, teacher_name, template_code, business_type,
                    title, description, status, task_items, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
            """, (
                new_todo_id, teacher['teacher_id'], teacher['name'], template_code,
                'retirement_reminder',
                f"{teacher['name']} - 到龄退休审批（{teacher['retirement_age']}岁）",
                f"教师 {teacher['name']}（{teacher['gender']}）将于 {teacher['retirement_date'].strftime('%Y年%m月%d日')} 年满{teacher['retirement_age']}周岁，距离现在还有 {teacher['days_until']} 天",
                'pending',
                json.dumps(task_items)
            ))
            
            logger.info(f"    [创建] {teacher['name']}({teacher['gender']}) - 退休日期: {teacher['retirement_date']}, 还剩{teacher['days_until']}天")
        
        conn.commit()
        logger.info(f"[完成] 新建到龄退休提醒待办: {created_count}")
        
    except Exception as e:
        conn.rollback()
        logger.error(f"[错误] 扫描到龄退休提醒待办失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cursor.close()
        conn.close()

def start_scheduler():
    """启动定时调度器"""
    scheduler = BackgroundScheduler()
    
    # 每天凌晨2:00执行扫描
    scheduler.add_job(
        scan_octogenarian_subsidy,
        CronTrigger(hour=2, minute=0),
        id='octogenarian_scan',
        name='80周岁高龄补贴扫描',
        replace_existing=True
    )
    
    scheduler.add_job(
        scan_retirement_reminder,
        CronTrigger(hour=2, minute=0),
        id='retirement_scan',
        name='到龄退休提醒扫描',
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("[启动] 待办任务定时调度器已启动，每天凌晨2:00执行扫描")
    
    return scheduler

if __name__ == '__main__':
    # 测试运行一次
    logger.info("=" * 60)
    logger.info("手动执行待办任务扫描")
    logger.info("=" * 60)
    scan_octogenarian_subsidy()
    logger.info("")
    scan_retirement_reminder()
