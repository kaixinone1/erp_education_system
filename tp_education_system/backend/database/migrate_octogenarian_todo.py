#!/usr/bin/env python3
"""
80周岁高龄补贴待办数据迁移脚本
- 从教师基础信息表中筛选即将年满80周岁的教师
- 与已导入的高龄老人补贴信息表进行比对
- 不在已导入表中的才推送待办
- 提前60天推送提醒
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

def get_80th_birthday(birth_date):
    """计算80周岁生日日期"""
    if not birth_date:
        return None
    return birth_date + relativedelta(years=80)

def migrate_octogenarian_todos():
    """迁移80周岁高龄补贴待办数据"""
    conn = psycopg2.connect(**DATABASE_CONFIG)
    cursor = conn.cursor()
    
    try:
        today = datetime.now().date()
        advance_days = 60  # 提前60天推送
        
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始迁移80周岁高龄补贴待办数据")
        print(f"  - 提前推送天数: {advance_days}天")
        print(f"  - 当前日期: {today}")
        
        # 1. 查询已导入的高龄老人补贴信息表中的身份证号码
        cursor.execute('SELECT 身份证号码 FROM "高龄老人补贴信息" WHERE 状态 != %s', ('死亡',))
        existing_ids = set(row[0] for row in cursor.fetchall())
        print(f"  - 已导入的高龄补贴人数: {len(existing_ids)}")
        
        # 2. 查询教师基础信息表中即将年满80周岁的教师
        cursor.execute("""
            SELECT 
                id,
                name,
                id_card,
                archive_birth_date,
                ethnicity,
                native_place,
                contact_phone
            FROM teacher_basic_info
            WHERE archive_birth_date IS NOT NULL
              AND id_card IS NOT NULL
              AND id_card != ''
            ORDER BY archive_birth_date
        """)
        
        teachers = cursor.fetchall()
        print(f"  - 教师基础信息表总人数: {len(teachers)}")
        
        # 3. 筛选符合条件的教师
        eligible_teachers = []
        for teacher in teachers:
            teacher_id, name, id_card, birth_date, ethnicity, native_place, phone = teacher
            
            if not birth_date:
                continue
                
            # 计算80周岁生日
            birthday_80 = get_80th_birthday(birth_date)
            if not birthday_80:
                continue
            
            # 检查是否在未来60天内满80周岁
            days_until_80 = (birthday_80 - today).days
            
            # 条件：80周岁生日在未来60天内，且尚未过去
            if 0 <= days_until_80 <= advance_days:
                # 检查是否已在高龄补贴表中
                if id_card not in existing_ids:
                    eligible_teachers.append({
                        'teacher_id': teacher_id,
                        'name': name,
                        'id_card': id_card,
                        'birth_date': birth_date,
                        'ethnicity': ethnicity,
                        'native_place': native_place,
                        'phone': phone,
                        'birthday_80': birthday_80,
                        'days_until': days_until_80
                    })
        
        print(f"  - 符合条件（即将满80周岁且未导入）的人数: {len(eligible_teachers)}")
        
        # 4. 查询或创建80周岁高龄补贴模板
        cursor.execute("""
            SELECT template_code FROM todo_templates 
            WHERE template_name = %s LIMIT 1
        """, ('80周岁高龄补贴申请',))
        
        template_result = cursor.fetchone()
        if template_result:
            template_code = template_result[0]
            print(f"  - 找到现有模板 CODE: {template_code}")
        else:
            # 创建模板
            template_code = 'OCTOGENARIAN_SUBSIDY'
            task_flow = [
                {"name": "联系教师家属", "completed": False},
                {"name": "收集申请材料", "completed": False},
                {"name": "填写申请表", "completed": False},
                {"name": "上报审批", "completed": False},
                {"name": "跟踪审批进度", "completed": False},
                {"name": "通知教师领取", "completed": False}
            ]
            cursor.execute("""
                INSERT INTO todo_templates (
                    template_code, template_name, business_type, description, 
                    task_flow, due_date_rule, default_priority, is_enabled, 
                    created_at, updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
            """, (
                template_code,
                '80周岁高龄补贴申请',
                'octogenarian_subsidy',
                '为即将年满80周岁的教师办理高龄补贴申请',
                json.dumps(task_flow),
                'birthday_plus_80',
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
            due_date = teacher['birthday_80']
            task_items = [
                {"name": "联系教师家属", "completed": False},
                {"name": "收集申请材料", "completed": False},
                {"name": "填写申请表", "completed": False},
                {"name": "上报审批", "completed": False},
                {"name": "跟踪审批进度", "completed": False},
                {"name": "通知教师领取", "completed": False}
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
                'octogenarian_subsidy',
                teacher['teacher_id'],
                teacher['name'],
                f"{teacher['name']} - 80周岁高龄补贴申请",
                f"教师 {teacher['name']} 将于 {teacher['birthday_80'].strftime('%Y年%m月%d日')} 年满80周岁，"
                f"距离现在还有 {teacher['days_until']} 天，请提前办理高龄补贴申请。",
                due_date,
                'pending',
                'high' if teacher['days_until'] <= 30 else 'normal',
                json.dumps(task_items)
            ))
            
            created_count += 1
            print(f"    [创建] {teacher['name']} - 80周岁日期: {teacher['birthday_80']}, 还剩{teacher['days_until']}天")
        
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
    result = migrate_octogenarian_todos()
    print(f"\n结果: {result}")
