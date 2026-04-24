from fastapi import APIRouter, Query
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import psycopg2
import json

router = APIRouter(prefix="/api")

def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        port="5432",
        database="taiping_education",
        user="taiping_user",
        password="taiping_password"
    )


def calculate_retirement_old_policy(birth_date, gender):
    """按旧政策计算退休日期"""
    if gender == '男':
        retirement_age = 60
    else:
        retirement_age = 55
    return birth_date + relativedelta(years=retirement_age)


def calculate_retirement_new_policy(birth_date, gender, personal_identity):
    """按新政策计算退休日期
    
    延迟月数公式：
    =IFS(
      (男), IF(出生日期<1976-09-01, INT(DATEDIF(2025-01-01, 原退休日期, "月")/4+1), 36),
      (女)且(非干部), IF(出生日期<1984-11-01, INT(DATEDIF(2025-01-01, 原退休日期, "月")/2+1), 60),
      (女)且(干部), IF(出生日期<1981-09-01, INT(DATEDIF(2025-01-01, 原退休日期, "月")/4+1), 36)
    )
    
    参数说明：
    - personal_identity: 个人身份，可能是"干部"、"工人"等
    """
    if not birth_date:
        return None, 0, None
    
    # 1. 判断是否干部（根据个人身份字段）
    is_cadre = (personal_identity == '干部')
    
    # 2. 原退休日期
    if gender == '男':
        original_age = 60
    elif is_cadre:
        original_age = 55  # 女干部55岁
    else:
        original_age = 50  # 女工人50岁
    
    original_date = birth_date + relativedelta(years=original_age)
    
    # 3. 计算从2025-01-01到原退休日期的月数
    base_date = date(2025, 1, 1)
    if original_date < base_date:
        months_from_2025 = 0
    else:
        months_from_2025 = (original_date.year - 2025) * 12 + original_date.month - 1
    
    # 4. 延迟月数
    delay = 0
    if gender == '男':
        if birth_date < date(1976, 9, 1):
            delay = min(int(months_from_2025 / 4 + 1), 36)
        else:
            delay = 36
    elif gender == '女':
        if is_cadre:
            # 女干部
            if birth_date < date(1981, 9, 1):
                delay = min(int(months_from_2025 / 4 + 1), 36)
            else:
                delay = 36
        else:
            # 女工人
            if birth_date < date(1984, 11, 1):
                delay = min(int(months_from_2025 / 2 + 1), 60)
            else:
                delay = 60
    
    new_date = original_date + relativedelta(months=delay)
    return original_date, delay, new_date


@router.get("/retirement/calculate")
async def calculate_retirement(
    estimate_type: str = Query('new', description='old or new'),
    start_date: str = Query(..., description='Start date'),
    end_date: str = Query(..., description='End date')
):
    """退休测算"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 退休状态列表
        retired_statuses = ['退休', '离休', '死亡', '去世', '调离', '离职']
        
        # 查询教师信息（排除已退休/离休/死亡等状态）
        # 关联教师单位表(通过unit_1获取单位ID)和个人身份表(通过ge_ren_shen_fen获取身份ID)
        # 关联字典表获取单位名称和个人身份名称
        cursor.execute("""
            SELECT 
                t.id, t.name, t.id_card, t.archive_birth_date, t.employment_status, t.is_cadre,
                u.unit_1 as unit_id,
                p.ge_ren_shen_fen as identity_id,
                du.unit as unit_name,
                dpi.ge_ren_shen_fen as identity_name
            FROM teacher_basic_info t
            LEFT JOIN teacher_unit u ON t.id_card = u.id_card
            LEFT JOIN teacher_personal_identity p ON t.id_card = p.id_card
            LEFT JOIN dict_unit_dictionary du ON u.unit_1 = du.id::varchar
            LEFT JOIN dict_personal_identity_dictionary dpi ON p.ge_ren_shen_fen = dpi.id::varchar
            WHERE t.id_card IS NOT NULL AND t.id_card != ''
              AND (t.employment_status IS NULL OR t.employment_status NOT IN %s)
            ORDER BY t.id
        """, (tuple(retired_statuses),))
        
        teachers = cursor.fetchall()
        results = []
        
        for row in teachers:
            teacher_id, name, id_card, archive_birth, emp_status, is_cadre, unit_id, identity_id, unit_name, identity_name = row
            
            # 获取出生日期（优先使用档案出生日期）
            birth_date = archive_birth
            if not birth_date and id_card and len(id_card) == 18:
                try:
                    year = int(id_card[6:10])
                    month = int(id_card[10:12])
                    day = int(id_card[12:14])
                    birth_date = date(year, month, day)
                except:
                    continue
            
            if not birth_date:
                continue
            
            # 获取性别
            gender = '男'
            if id_card and len(id_card) == 18:
                gender = '女' if int(id_card[16]) % 2 == 0 else '男'
            
            # 计算退休日期
            if estimate_type == 'old':
                orig_date = calculate_retirement_old_policy(birth_date, gender)
                delay = 0
                new_date = orig_date
            else:
                orig_date, delay, new_date = calculate_retirement_new_policy(
                    birth_date, gender, identity_name
                )
            
            if not new_date:
                continue
            
            # 按日期范围筛选
            if start_date and end_date:
                start = datetime.strptime(start_date, '%Y-%m-%d').date()
                end = datetime.strptime(end_date, '%Y-%m-%d').date()
                if not (start <= new_date <= end):
                    continue
            
            results.append({
                'teacher_id': teacher_id,
                'name': name,
                'id_card': id_card,
                'gender': gender,
                'birth_date': birth_date.isoformat() if birth_date else None,
                'is_cadre': identity_name if identity_name else (is_cadre or '否'),
                'personal_identity': identity_name,
                'employment_status': emp_status,
                'unit_name': unit_name if unit_name else emp_status,
                'original_retirement_date': orig_date.isoformat() if orig_date else None,
                'delay_months': delay,
                'new_retirement_date': new_date.isoformat() if new_date else None
            })
        
        return {
            'success': True,
            'data': results,
            'total': len(results)
        }
    
    except Exception as e:
        return {'success': False, 'message': str(e)}
    finally:
        cursor.close()
        conn.close()
