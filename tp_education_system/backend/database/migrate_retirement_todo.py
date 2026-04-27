#!/usr/bin/env python3
"""
到龄退休提醒待办数据迁移脚本
- 从教师基础信息表中筛选即将到龄退休的教师
- 排除任职状态已经是"退休"的教师
- 提前7周（49天）推送提醒
"""
import psycopg2
import json
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

DATABASE_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "database": "taiping_education",
    "user": "taiping_user",
    "password": "taiping_password"
}

def get_retirement_date(birth_date, gender):
    """
    计算退休年龄日期
    - 男：60周岁
    - 女：55周岁
    """
    if not birth_date:
        return None
    
    # 根据性别确定退休年龄
    if gender and '女' in str(gender):
        retirement_age = 55
    else:
        retirement_age = 60
    
    return birth_date + relativedelta(years=retirement_age)

def get_gender_from_id_card(id_card):
    """从身份证号获取性别"""
    if not id_card or len(id_card) != 18:
        return None
    # 第17位数字，奇数为男，偶数为女
    try:
        gender_code = int(id_card[16])
        return '女' if gender_code % 2 == 0 else '男'
    except:
        return None

def migrate_retirement_todos():
    """迁移到龄退休提醒待办数据"""
    conn = psycopg2.connect(**DATABASE_CONFIG)
    cursor = conn.cursor()
    
    try:
        today = datetime.now().date()
        advance_days = 49  # 提前7周 = 49天推送
        
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始到龄退休提醒待办数据迁移")
        print(f"  - 提前推送天数: {advance_days}天（7周）")
        print(f"  - 当前日期: {today}")
        
        # 1. 查询任职状态字典，找到"退休"状态的值
        cursor.execute("""
            SELECT employment_status FROM dict_dictionary 
            WHERE employment_status = %s OR status_code = %s
            LIMIT 1
        """, ('退休', '退休'))
        
        result = cursor.fetchone()
        retired_status = result[0] if result else '退休'
        print(f"  - 退休状态值: {retired_status}")
        
        # 2. 查询教师基础信息表
        # 排除任职状态为"退休"的教师
        cursor.execute("""
            SELECT 
                id,
                name,
                id_card,
                archive_birth_date,
                employment_status,
                contact_phone
            FROM teacher_basic_info
            WHERE archive_birth_date IS NOT NULL
              AND id_card IS NOT NULL
              AND id_card != ''
              AND (employment_status IS NULL OR employment_status != %s)
            ORDER BY archive_birth_date
        """, (retired_status,))
        
        teachers = cursor.fetchall()
        print(f"  - 未退休教师人数: {len(teachers)}")
        
        # 3. 筛选符合条件的教师（即将在未来49天内到龄退休）
        eligible_teachers = []
        for teacher in teachers:
            teacher_id, name, id_card, birth_date, work_status, phone = teacher
            
            if not birth_date:
                continue
            
            # 从身份证号获取性别
            gender = get_gender_from_id_card(id_card)
            if not gender:
                gender = '男'  # 默认男性
            
            # 计算退休日期
            retirement_date = get_retirement_date(birth_date, gender)
            if not retirement_date:
                continue
            
            # 检查是否在未来49天内到龄退休
            days_until_retirement = (retirement_date - today).days
            
            # 条件：退休日期在未来49天内，且尚未过去
            if 0 <= days_until_retirement <= advance_days:
                eligible_teachers.append({
                    'teacher_id': teacher_id,
                    'name': name,
                    'id_card': id_card,
                    'birth_date': birth_date,
                    'gender': gender,
                    'phone': phone,
                    'work_status': work_status,
                    'retirement_date': retirement_date,
                    'days_until': days_until_retirement,
                    'retirement_age': 55 if gender == '女' else 60
                })
        
        print(f"  - 符合条件（即将到龄退休）的人数: {len(eligible_teachers)}")
        
        # 4. 查询或创建到龄退休提醒模板
        cursor.execute("""
            SELECT template_code FROM todo_templates 
            WHERE template_name = %s LIMIT 1
        """, ('到龄退休审批',))
        
        template_result = cursor.fetchone()
        if template_result:
            template_code = template_result[0]
            print(f"  - 找到现有模板 CODE: {template_code}")
        else:
            # 创建模板
            template_code = 'RETIREMENT_APPROVAL'
            task_flow = [
                {"name": "通知教师本人", "completed": False},
                {"name": "收集退休材料", "completed": False},
                {"name": "填写退休申请表", "completed": False},
                {"name": "单位审核", "completed": False},
                {"name": "上报主管部门", "completed": False},
                {"name": "审批跟踪", "completed": False},
                {"name": "办理退休手续", "completed": False},
                {"name": "通知教师领取退休证", "completed": False}
            ]
            cursor.execute("""
                INSERT INTO todo_templates (
                    template_code, template_name, business_type, description, 
                    task_flow, due_date_rule, default_priority, is_enabled, 
                    created_at, updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
            """, (
                template_code,
                '到龄退休审批',
                'retirement_reminder',
                '为即将到龄退休的教师办理退休审批手续',
                json.dumps(task_flow),
                'retirement_date',
                'normal',
                True
            ))
            print(f"  - 创建新模板 CODE: {template_code}")
        
        # 5. 为符合条件的教师创建待办事项
        created_count = 0
        skipped_count = 0
        
        for teacher in eligible_teachers:
            # 检查是否已存在待办
            cursor.execute("""
                SELECT id FROM todo_items 
                WHERE teacher_id = %s 
                  AND template_id = %s
                  AND status IN ('pending', 'in_progress')
            """, (teacher['teacher_id'], template_code))
            
            if cursor.fetchone():
                skipped_count += 1
                continue
            
            # 创建待办事项
            due_date = teacher['retirement_date']
            task_items = [
                {"name": "通知教师本人", "completed": False},
                {"name": "收集退休材料", "completed": False},
                {"name": "填写退休申请表", "completed": False},
                {"name": "单位审核", "completed": False},
                {"name": "上报主管部门", "completed": False},
                {"name": "审批跟踪", "completed": False},
                {"name": "办理退休手续", "completed": False},
                {"name": "通知教师领取退休证", "completed": False}
            ]
            
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
                due_date,
                'pending',
                'high' if teacher['days_until'] <= 14 else 'normal',
                json.dumps(task_items)
            ))
            
            created_count += 1
            print(f"    [创建] {teacher['name']}({teacher['gender']}) - 退休日期: {teacher['retirement_date']}, 还剩{teacher['days_until']}天")
        
        conn.commit()
        
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 迁移完成")
        print(f"  - 新建待办: {created_count}")
        print(f"  - 跳过（已存在）: {skipped_count}")
        
        return {
            'status': 'success',
            'created': created_count,
            'skipped': skipped_count,
            'total_eligible': len(eligible_teachers)
        }
        
    except Exception as e:
        conn.rollback()
        print(f"[错误] 迁移失败: {e}")
        import traceback
        traceback.print_exc()
        return {'status': 'error', 'message': str(e)}
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    result = migrate_retirement_todos()
    print(f"\n结果: {result}")
