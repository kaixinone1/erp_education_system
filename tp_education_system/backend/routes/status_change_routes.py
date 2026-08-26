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


def _convert_to_bool(value):
    """将各种可能的值转换为布尔值，专门处理数据库boolean类型转换"""
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip() in ('是', '1', 'true', 'True', 'yes', 'Yes', 'Y', 'y')
    if isinstance(value, (int, float)):
        return bool(value)
    return None


def _to_chinese_bool(value):
    """将各种可能的值转换为中文"是"/"否"，面向用户显示"""
    if value is None:
        return ''
    if isinstance(value, bool):
        return '是' if value else '否'
    if isinstance(value, str):
        v = value.strip()
        if v in ('是', '1', 'true', 'True', 'yes', 'Yes', 'Y', 'y'):
            return '是'
        if v in ('否', '0', 'false', 'False', 'no', 'No', 'N', 'n'):
            return '否'
        return v
    if isinstance(value, (int, float)):
        return '是' if value else '否'
    return ''


def _build_retirement_report_data(cursor, teacher_id, teacher_row, id_card, education_row):
    """构建退休呈报表完整数据 - 从多个数据源自动汇集
    
    数据源：
    1. teacher_basic_info - 基础信息、出生日期
    2. post_appointment_info - 职务、职称
    3. salary_data - 三个时间点的职务岗位和级别薪级
    4. retirement_info - 退休补充信息（动态查询实际列）
    """
    from datetime import datetime as dt
    import re
    
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
    # 先加载字典表数据
    cursor.execute("SELECT id, post FROM dict_dictionary_personal ORDER BY id")
    dict_personal = {row[0]: row[1] for row in cursor.fetchall()}  # id -> 职称名称
    
    cursor.execute("SELECT id, post_level FROM dict_grade_dictionary ORDER BY id")
    dict_grade = {row[0]: row[1] for row in cursor.fetchall()}  # id -> 岗位等级名称（如"七级专技"）
    
    # 岗位等级名称（如"四级专技"） -> 职务（正高级/副高级/中级/初级）
    POST_LEVEL_TO_TITLE = {
        '四级专技': '正高级', '四级义教': '正高级',
        '五级专技': '副高级', '五级义教': '副高级',
        '六级专技': '副高级', '六级义教': '副高级',
        '七级专技': '副高级', '七级义教': '副高级',
        '八级专技': '中级', '八级义教': '中级',
        '九级专技': '中级', '九级义教': '中级',
        '十级专技': '中级', '十级义教': '中级',
        '11级专技': '初级', '11级义教': '初级',
        '12级专技': '初级', '12级义教': '初级',
        '13级专技': '初级', '13级义教': '初级',
    }
    
    position_title = None  # 职务（正高级/副高级/中级/初级）
    professional_title = None  # 职称（高级教师/一级教师/二级教师/三级教师）
    duty = None  # 岗位
    
    cursor.execute("""
        SELECT post_1, post_level_1, professional_title, job_title
        FROM post_appointment_info
        WHERE id_card = %s
        ORDER BY id DESC LIMIT 1
    """, (id_card,))
    post_row = cursor.fetchone()
    if post_row:
        post_1_val = post_row[0]   # 字典id -> 职称（高级教师/一级教师等）
        post_level_1_val = post_row[1]  # 字典id -> 岗位等级名称（如"七级专技"）
        prof_title_val = post_row[2]    # 已评职称（如"高级"）
        job_title_val = post_row[3]     # 原聘职务（如"六级专技"）
        
        # 职称（专业技术职称）：优先从 post_1 字典转换，否则取 professional_title，再取 job_title
        if post_1_val is not None:
            try:
                post_1_id = int(post_1_val)
                professional_title = dict_personal.get(post_1_id)
            except (ValueError, TypeError):
                pass
        if not professional_title:
            professional_title = prof_title_val if prof_title_val else job_title_val
        
        # 职务（正高级/副高级/中级/初级）：先从 post_level_1 字典转换为岗位等级名称，再映射
        if post_level_1_val is not None:
            try:
                level_id = int(post_level_1_val)
                level_name = dict_grade.get(level_id)  # 如"七级专技"
                if level_name:
                    position_title = POST_LEVEL_TO_TITLE.get(level_name)
            except (ValueError, TypeError):
                pass
        # 如果字典转换失败，尝试从 job_title 直接解析（如"六级专技"）
        if not position_title and job_title_val:
            position_title = POST_LEVEL_TO_TITLE.get(str(job_title_val))
        
        duty = None
    
    # ==================== 三、单位岗位区（最新工资包数据） ====================
    # 人员分类：根据 job_title_post 判断
    # 机关工人、事业管理（包含"管理"）、事业专技（包含"专技"或"义教"）、事业工勤（包含"技工"）
    personnel_category = 'unknown'  # 人员分类：management/technical/worker/other
    
    def classify_personnel(job_title_str):
        """根据职务岗位字符串判断人员分类"""
        if not job_title_str:
            return 'unknown'
        s = str(job_title_str)
        if '管理' in s:
            return 'management'
        if '专技' in s or '义教' in s:
            return 'technical'
        if '技工' in s:
            return 'worker'
        return 'other'
    
    salary_time_points = {
        '2014年9月30日': {'job_title': None, 'salary_level': None, 'salary': None, 'position_salary': None},
        '最后一次职务升降时间': {'time': None, 'job_title': None, 'salary_level': None, 'salary': None, 'position_salary': None},
        '退休时': {'job_title': None, 'salary_level': None, 'salary': None, 'position_salary': None},
    }
    
    # 查询该教师的所有工资记录
    # "最新工资包数据" 在数据库中对应的表名是 salary_info，身份证列是 id_card
    cursor.execute("""
        SELECT job_title_post, salary_level, time, salary, salary_1, type, type_1
        FROM salary_info
        WHERE id_card = %s
        ORDER BY time
    """, (id_card,))
    salary_rows = cursor.fetchall()
    
    if salary_rows:
        # 先确定退休时的时间点（最大起薪时间），用于后续人员分类
        max_time_row = max(salary_rows, key=lambda r: r[2] if r[2] else '')
        
        # 确定人员分类（以退休时职务岗位为准）
        personnel_category = classify_personnel(max_time_row[0])
        
        # 1) 2014年9月30日：起薪时间=2014-10-01
        # 注意：salary_data表中 salary列=岗位工资，salary_1列=薪级工资
        for row in salary_rows:
            if row[2] and str(row[2]) == '2014-10-01':
                salary_time_points['2014年9月30日']['job_title'] = row[0]
                salary_time_points['2014年9月30日']['salary_level'] = row[1]
                salary_time_points['2014年9月30日']['position_salary'] = row[3]  # salary列=岗位工资
                salary_time_points['2014年9月30日']['salary'] = row[4]           # salary_1列=薪级工资
                break
        
        # 2) 最后一次职务升降时间：职务岗位最高一级（数字最小）对应起薪时间中的最小日期值
        def parse_job_rank(job_title):
            """解析职务岗位等级，返回数字以便比较（数字越小，级别越高）"""
            if not job_title:
                return 999
            chinese_map = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9, '十': 10}
            for ch, num in chinese_map.items():
                if ch in str(job_title):
                    return num
            match = re.search(r'(\d+)', str(job_title))
            if match:
                return int(match.group(1))
            return 999
        
        # 找出最高职务岗位等级（数字最小）
        best_rank = 999
        for row in salary_rows:
            rank = parse_job_rank(row[0])
            if rank < best_rank:
                best_rank = rank
        
        # 在最高等级的所有记录中，找起薪时间最小的那条
        best_rows = [r for r in salary_rows if parse_job_rank(r[0]) == best_rank]
        if best_rows:
            best_row = min(best_rows, key=lambda r: r[2] if r[2] else '9999-99-99')
            salary_time_points['最后一次职务升降时间']['time'] = best_row[2]
            salary_time_points['最后一次职务升降时间']['job_title'] = best_row[0]
            salary_time_points['最后一次职务升降时间']['salary_level'] = best_row[1]
            salary_time_points['最后一次职务升降时间']['position_salary'] = best_row[3]  # salary列=岗位工资
            salary_time_points['最后一次职务升降时间']['salary'] = best_row[4]           # salary_1列=薪级工资
        
        # 3) 退休时：最大起薪时间（已在上面计算）
        salary_time_points['退休时']['job_title'] = max_time_row[0]
        salary_time_points['退休时']['salary_level'] = max_time_row[1]
        salary_time_points['退休时']['position_salary'] = max_time_row[3]  # salary列=岗位工资
        salary_time_points['退休时']['salary'] = max_time_row[4]           # salary_1列=薪级工资
    
    # ==================== 四、退休补充信息（动态查询实际列） ====================
    # 退休补充信息表名：优先查 tui_xiu_bu_chong_xin_xi（新表），否则 retirement_info（旧表）
    ri_table_name = 'tui_xiu_bu_chong_xin_xi'
    cursor.execute("""
        SELECT EXISTS (
            SELECT 1 FROM information_schema.tables 
            WHERE table_name = 'tui_xiu_bu_chong_xin_xi'
        )
    """)
    if not cursor.fetchone()[0]:
        ri_table_name = 'retirement_info'
    
    # 动态获取退休补充信息表的所有列名
    cursor.execute("""
        SELECT column_name FROM information_schema.columns
        WHERE table_name = %s ORDER BY ordinal_position
    """, (ri_table_name,))
    ri_columns = [r[0] for r in cursor.fetchall()]
    
    # 查询退休补充信息
    cursor.execute(f"""
        SELECT * FROM "{ri_table_name}"
        WHERE id_card = %s ORDER BY id DESC LIMIT 1
    """, (id_card,))
    ri_row = cursor.fetchone()
    
    # 字段名映射（数据库列名 -> 返回字典key）
    # 覆盖新旧表的所有可能字段名
    RI_FIELD_MAP = {
        # 基础字段
        'name': '姓名',
        'id_card': '身份证号码',
        # 旧表字段
        'children': '是否独生子女',
        'name_birth_date': '供养亲属',
        # 新表字段（tui_xiu_bu_chong_xin_xi）
        'retirement_reason': '退休原因',
        'year_month': '自何年何月',
        'year_month_1': '至何年何月',
        'unit_3': '工作经历',
        'zheng_ming_ren_ji_qi_zhu_zhi': '证明人及其住址',
        'xian_zhu_zhi': '现住址',
        'retired': '退休后居住地址',
        'retirement_fee_unit': '发给退休费的单位',
        # 可能的其他字段名
        '在何单位任何职': '工作经历',
        '证明人及住址': '证明人及其住址',
        '退休后居住地': '退休后居住地址',
        '现居住地址': '现住址',
    }
    
    retirement_info = {}
    if ri_row:
        for i, col_name in enumerate(ri_columns):
            key = RI_FIELD_MAP.get(col_name, col_name)
            retirement_info[key] = ri_row[i]
    
    # 安全获取退休补充信息字段（不存在则返回None）
    def get_ri_field(field_name):
        return retirement_info.get(field_name)
    
    # ==================== 五、从党员信息表获取入党年月 ====================
    join_party_date = None
    if id_card:
        try:
            cursor.execute(
                'SELECT join_party_date FROM zao_yang_shi_tai_ping_zhen_zhong_xin_xue_xiao_dang_yuan_xin_xi_biao WHERE id_card = %s LIMIT 1',
                (id_card,)
            )
            party_row = cursor.fetchone()
            if party_row and party_row[0]:
                join_party_date = party_row[0]
        except Exception:
            pass
    
    # ==================== 六、构建返回数据 ====================
    # 根据人员分类，将三个时间点的数据映射到对应的退休呈报表字段
    # 退休呈报表字段命名规则：
    #   时间点1(2014年9月30日): 事业管理→岗位1, 事业专技→岗位2, 事业工勤→岗位3
    #   时间点2(最后一次职务升降): 事业管理→岗位4, 事业专技→岗位5, 事业工勤→岗位6
    #   时间点3(退休时): 事业管理→岗位7, 事业专技→岗位8, 事业工勤→岗位9
    
    tp1 = salary_time_points['2014年9月30日']
    tp2 = salary_time_points['最后一次职务升降时间']
    tp3 = salary_time_points['退休时']
    
    # 分类岗位字段映射
    CATEGORY_FIELDS = {
        'management': {
            'tp1_post': '事业管理岗位1', 'tp1_level': '薪级1', 'tp1_duty': '对应原职务1',
            'tp2_post': '事业管理岗位4', 'tp2_level': '薪级4', 'tp2_duty': '对应原职务4',
            'tp3_post': '退休时事业管理岗位7', 'tp3_level': '薪级7', 'tp3_duty': '对应原职务7',
        },
        'technical': {
            'tp1_post': '事业专技岗位2', 'tp1_level': '薪级2', 'tp1_duty': '对应原职务2',
            'tp2_post': '事业专技岗位5', 'tp2_level': '薪级5', 'tp2_duty': '对应原职务5',
            'tp3_post': '退休时事业专技岗位8', 'tp3_level': '薪级8', 'tp3_duty': '对应原职务8',
        },
        'worker': {
            'tp1_post': '事业工勤岗位3', 'tp1_level': '薪级3', 'tp1_duty': '对应技术等级3',
            'tp2_post': '事业工勤岗位6', 'tp2_level': '薪级6', 'tp2_duty': '对应技术等级6',
            'tp3_post': '退休时事业工勤岗位9', 'tp3_level': '薪级9', 'tp3_duty': '对应技术等级9',
        },
    }
    
    cat_fields = CATEGORY_FIELDS.get(personnel_category, CATEGORY_FIELDS['technical'])
    
    result = {
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
        # 退休补充信息（动态获取）
        "退休原因": get_ri_field('退休原因'),
        # 是否独生子女：保持原始值（数据库列类型为boolean）
        "是否独生子女": get_ri_field('是否独生子女'),
        "供养亲属": get_ri_field('供养亲属'),
        "现住址": get_ri_field('现住址'),
        "退休后居住地址": get_ri_field('退休后居住地址'),
        "发给退休费的单位": get_ri_field('发给退休费的单位'),
        "工作经历": get_ri_field('工作经历'),
        "自何年何月": get_ri_field('自何年何月'),
        "至何年何月": get_ri_field('至何年何月'),
        "所在单位及职务": get_ri_field('工作经历') or get_ri_field('所在单位及职务'),
        "证明人及其住址": get_ri_field('证明人及其住址') or get_ri_field('证明人及住址'),
        "直系亲属供养情况": get_ri_field('供养亲属') or get_ri_field('直系亲属供养情况'),
        "单位意见": None,
        "直系亲属信息": get_ri_field('供养亲属') or get_ri_field('直系亲属供养情况') or get_ri_field('直系亲属信息'),
        "入党年月": join_party_date,
        "退休时间": None,
        "个人身份": None,
        "备注": None,
        # 人员分类
        "人员分类": personnel_category,
        # 通用薪级和岗位（退休时）
        "薪级工资": tp3['salary'],
        "岗位工资": tp3['position_salary'],
        "技术等级": None,
        "最后一次职务升降时间": tp2['time'],
        # 分类岗位字段（根据人员分类动态填充）
        cat_fields['tp1_post']: tp1['job_title'],
        cat_fields['tp1_level']: tp1['salary_level'],
        cat_fields['tp1_duty']: tp1['job_title'],
        cat_fields['tp2_post']: tp2['job_title'],
        cat_fields['tp2_level']: tp2['salary_level'],
        cat_fields['tp2_duty']: tp2['job_title'],
        cat_fields['tp3_post']: tp3['job_title'],
        cat_fields['tp3_level']: tp3['salary_level'],
        cat_fields['tp3_duty']: tp3['job_title'],
        # 保留兼容旧字段名
        "2014年9月30日职务岗位": tp1['job_title'],
        "2014年9月30日级别薪级": tp1['salary_level'],
        "2014年9月30日薪级工资": tp1['salary'],
        "2014年9月30日岗位工资": tp1['position_salary'],
        "最后一次职务升降岗位": tp2['job_title'],
        "最后一次职务升降薪级": tp2['salary_level'],
        "最后一次职务升降薪级工资": tp2['salary'],
        "最后一次职务升降岗位工资": tp2['position_salary'],
        "退休时职务岗位": tp3['job_title'],
        "退休时级别薪级": tp3['salary_level'],
        "退休时薪级工资": tp3['salary'],
        "退休时岗位工资": tp3['position_salary'],
    }
    
    return result


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


# ==================== 标签同步常量 ====================

# 标签ID常量（与 personal_dict_dictionary 表对应）
TAG_IDS = {
    '基础工资': 1, '绩效工资': 2, '乡镇补贴': 3, '岗位聘用': 4,
    '新机制': 5, '年度考核': 6, '人事年报': 7, '工资年报': 8,
    '乡村定向': 9, '延迟退休': 10, 'gcdy': 11, 'dj': 12,
    '组织关系挂靠': 26, 'gqty': 13, 'tj': 14, '群众': 15,
    '在职': 16, '调出': 17, '调离': 18, '辞职': 19,
    '借调': 20, '离休': 21, '退休': 22, '去世': 23,
    '病休': 24, '病假': 25,
}

# 政治面貌标签（退休/调离时保留，包含共产党员、党籍、共青团员、团籍、群众）
POLITICAL_TAG_IDS = {11, 12, 13, 14, 15}  # gcdy, dj, gqty, tj, 群众

# 调离时保留至次年自然年的标签
TRANSFER_AWAY_KEEP_TAGS = {6, 7, 8}  # 年度考核, 人事年报, 工资年报


def _sync_tags_on_status_change(cursor, teacher_id, teacher_name, old_status, target_status, transfer_direction=None):
    """
    根据任职状态变更同步标签关系
    
    参数:
        cursor: 数据库游标
        teacher_id: 教师ID
        teacher_name: 教师姓名
        old_status: 变更前状态
        target_status: 变更后状态
        transfer_direction: 调出去向（'外乡镇' 或 '市直单位'），仅调出时需要
    
    返回:
        {"synced": bool, "actions": [str], "needs_manual": bool}
    """
    actions = []
    needs_manual = False

    # 获取当前标签
    cursor.execute(
        "SELECT tag_id FROM employee_tag_relations WHERE employee_id = %s",
        (teacher_id,)
    )
    current_tags = {row[0] for row in cursor.fetchall()}

    tags_to_remove = set()
    tags_to_add = set()

    if target_status == '退休':
        # 检查参加工作日期：1949年9月30日之前参加革命工作的，确定为离休
        cursor.execute('SELECT "参加工作日期" FROM teacher_basic_info WHERE id = %s', (teacher_id,))
        work_row = cursor.fetchone()
        work_date = work_row[0] if work_row else None
        
        is_retire_from_work = False
        if work_date:
            try:
                from datetime import datetime as dt
                d = dt.strptime(str(work_date)[:10], '%Y-%m-%d')
                if d < dt(1949, 10, 1):
                    is_retire_from_work = True
            except:
                pass
        
        if is_retire_from_work:
            # 离休
            tags_to_remove.add(TAG_IDS['在职'])
            tags_to_add.add(TAG_IDS['离休'])
            actions.append(f"离休（1949年9月30日前参加革命工作）：取消在职标签，添加离休标签")
        else:
            # 正常退休
            tags_to_remove.add(TAG_IDS['在职'])
            tags_to_add.add(TAG_IDS['退休'])
            actions.append(f"退休：取消在职标签，添加退休标签，保留党团标签")

    elif target_status == '去世':
        tags_to_remove = current_tags.copy()
        tags_to_add.add(TAG_IDS['去世'])
        actions.append(f"去世：取消全部标签，添加去世标签")

    elif target_status == '调出':
        tags_to_remove.add(TAG_IDS['在职'])
        tags_to_add.add(TAG_IDS['调出'])

        if transfer_direction == '外乡镇':
            tags_to_remove.add(TAG_IDS['绩效工资'])
            actions.append(f"调出（外乡镇）：取消在职、绩效工资标签")
        elif transfer_direction == '市直单位':
            tags_to_remove.add(TAG_IDS['绩效工资'])
            tags_to_remove.add(TAG_IDS['乡镇补贴'])
            actions.append(f"调出（市直单位）：取消在职、绩效工资、乡镇补贴标签")
        else:
            actions.append(f"调出：取消在职标签，其他标签待确认")
        needs_manual = True

    elif target_status == '调离':
        immediate_remove = {
            TAG_IDS['基础工资'], TAG_IDS['绩效工资'], TAG_IDS['乡镇补贴'],
            TAG_IDS['岗位聘用'], TAG_IDS['新机制'], TAG_IDS['乡村定向'],
            TAG_IDS['延迟退休'], TAG_IDS['在职'],
        }
        tags_to_remove.update(immediate_remove)
        tags_to_add.add(TAG_IDS['调离'])
        actions.append(f"调离：取消基础工资、绩效工资、乡镇补贴、岗位聘用、新机制、乡村定向、延迟退休、在职标签")
        actions.append(f"调离：保留年度考核、人事年报、工资年报至次年自然年，保留党团标签")
        needs_manual = True

    elif target_status == '离休':
        tags_to_remove.add(TAG_IDS['在职'])
        tags_to_add.add(TAG_IDS['离休'])
        actions.append(f"离休：取消在职标签，添加离休标签，保留党团标签")

    elif target_status == '在职':
        # 恢复为在职状态，清除所有非在职状态标签
        non_active_tags = {
            TAG_IDS['调出'], TAG_IDS['调离'], TAG_IDS['辞职'],
            TAG_IDS['借调'], TAG_IDS['离休'], TAG_IDS['退休'],
            TAG_IDS['去世'], TAG_IDS['病休'], TAG_IDS['病假'],
        }
        tags_to_remove.update(non_active_tags)
        tags_to_add.add(TAG_IDS['在职'])
        actions.append(f"恢复在职：清除非在职状态标签，添加在职标签")

    # 执行标签变更
    removed_count = 0
    for tag_id in tags_to_remove:
        if tag_id in current_tags:
            cursor.execute(
                "DELETE FROM employee_tag_relations WHERE employee_id = %s AND tag_id = %s",
                (teacher_id, tag_id)
            )
            removed_count += 1

    added_count = 0
    for tag_id in tags_to_add:
        if tag_id not in current_tags or tag_id in tags_to_remove:
            cursor.execute("""
                INSERT INTO employee_tag_relations (employee_id, tag_id)
                VALUES (%s, %s)
                ON CONFLICT (employee_id, tag_id) DO NOTHING
            """, (teacher_id, tag_id))
            added_count += 1

    result = {
        "synced": True,
        "actions": actions,
        "needs_manual": needs_manual,
        "removed_count": removed_count,
        "added_count": added_count,
    }

    logger.info(f"标签同步完成: {teacher_name}, 状态={target_status}, "
                f"移除{removed_count}个, 添加{added_count}个")

    return result


def _sync_political_tags(cursor, teacher_id, id_card):
    """
    根据 id_card 表中的政治面貌数据同步政治标签（共青团员、团籍、群众）
    
    数据源：id_card 表（通过身份证号关联）
    判定规则：
      - 共青团员 (tag_id=13): id_card.league_member = '是'
      - 团籍 (tag_id=14): id_card.league_member = '是'
      - 群众 (tag_id=15): id_card.party_member != '是' AND id_card.league_member != '是'
      - 共产党员 (tag_id=11) 和 党籍 (tag_id=12) 由党员信息表独立判定，此处不覆盖
    
    参数:
        cursor: 数据库游标
        teacher_id: 教师ID
        id_card: 教师身份证号码
    
    返回:
        {"synced": bool, "added": [int], "removed": [int]}
    """
    if not id_card:
        return {"synced": False, "added": [], "removed": [], "reason": "无身份证号"}

    # 查询 id_card 表中的政治面貌数据
    cursor.execute(
        'SELECT party_member, league_member, tuan_ji, masses FROM id_card WHERE id_card = %s',
        (id_card,)
    )
    row = cursor.fetchone()
    if not row:
        return {"synced": False, "added": [], "removed": [], "reason": "id_card表中无记录"}

    party_member = row[0]   # 共产党员
    league_member = row[1]  # 共青团员
    tuan_ji = row[2]        # 团籍
    masses = row[3]         # 群众

    def _is_yes(val):
        """判断字段值是否为'是'"""
        if val is None:
            return False
        return str(val).strip() == '是'

    is_party = _is_yes(party_member)
    is_league = _is_yes(league_member)
    is_tuan_ji = _is_yes(tuan_ji)
    is_masses = _is_yes(masses)

    # 获取当前政治标签（11-15）
    cursor.execute(
        "SELECT tag_id FROM employee_tag_relations WHERE employee_id = %s AND tag_id IN (13, 14, 15)",
        (teacher_id,)
    )
    current_political = {row[0] for row in cursor.fetchall()}

    tags_to_add = set()
    tags_to_remove = set()

    # 共青团员判定
    if is_league:
        tags_to_add.add(TAG_IDS['gqty'])  # 13
    else:
        tags_to_remove.add(TAG_IDS['gqty'])

    # 团籍判定（优先使用 tuan_ji 字段，若为空则与共青团员一致）
    if is_tuan_ji or is_league:
        tags_to_add.add(TAG_IDS['tj'])  # 14
    else:
        tags_to_remove.add(TAG_IDS['tj'])

    # 群众判定：非党员且非团员
    if not is_party and not is_league:
        tags_to_add.add(TAG_IDS['群众'])  # 15
    else:
        tags_to_remove.add(TAG_IDS['群众'])

    # 执行删除
    removed_ids = []
    for tag_id in tags_to_remove:
        if tag_id in current_political:
            cursor.execute(
                "DELETE FROM employee_tag_relations WHERE employee_id = %s AND tag_id = %s",
                (teacher_id, tag_id)
            )
            removed_ids.append(tag_id)

    # 执行添加
    added_ids = []
    for tag_id in tags_to_add:
        if tag_id not in current_political:
            cursor.execute("""
                INSERT INTO employee_tag_relations (employee_id, tag_id)
                VALUES (%s, %s)
                ON CONFLICT (employee_id, tag_id) DO NOTHING
            """, (teacher_id, tag_id))
            added_ids.append(tag_id)

    return {
        "synced": True,
        "added": added_ids,
        "removed": removed_ids,
    }


@router.post("/process")
async def process_status_change(data: dict[str, Any]):
    """
    处理教师状态变更
    当状态变更为退休时，自动汇集退休呈报表数据并创建待办工作清单
    同时自动同步标签关系管理表
    """
    try:
        teacher_id = data.get("teacher_id")
        teacher_name = data.get("teacher_name")
        source_status = data.get("source_status")
        target_status = data.get("target_status")
        transfer_direction = data.get("transfer_direction")  # 调出去向
        
        if not teacher_id or not target_status:
            raise HTTPException(status_code=400, detail="缺少必要参数")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 获取变更前的状态、教师姓名和身份证号码
        cursor.execute("""
            SELECT "任职状态", "姓名", "身份证号码" FROM teacher_basic_info WHERE id = %s
        """, (teacher_id,))
        row = cursor.fetchone()
        old_status = row[0] if row else None
        teacher_name = data.get("teacher_name") or (row[1] if row else "未知")
        teacher_id_card = row[2] if row else None
        
        # 更新教师状态，同时更新对应日期字段
        from datetime import date as dt_date
        today = dt_date.today()
        
        # 退休/离休判定：1949年9月30日前参加革命工作的为离休
        actual_target_status = target_status
        if target_status == '退休':
            cursor.execute(
                'SELECT "参加工作日期" FROM teacher_basic_info WHERE id = %s',
                (teacher_id,)
            )
            work_row = cursor.fetchone()
            if work_row and work_row[0]:
                try:
                    from datetime import datetime as dt
                    d = dt.strptime(str(work_row[0])[:10], '%Y-%m-%d')
                    if d < dt(1949, 10, 1):
                        actual_target_status = '离休'
                        logger.info(
                            f"教师 {teacher_name}(ID={teacher_id}) 参加工作日期 {work_row[0]} "
                            f"在1949年9月30日前，自动判定为离休"
                        )
                except:
                    pass
        
        update_sql = 'UPDATE teacher_basic_info SET "任职状态" = %s'
        update_params = [actual_target_status]
        
        if target_status == '调出' and transfer_direction:
            update_sql += ', "调出去向" = %s, "调出日期" = %s'
            update_params.extend([transfer_direction, today])
        elif target_status == '调离':
            update_sql += ', "调离日期" = %s'
            update_params.append(today)
        elif actual_target_status == '退休':
            update_sql += ', "退休日期" = %s'
            update_params.append(today)
        elif actual_target_status == '离休':
            update_sql += ', "退休日期" = %s'
            update_params.append(today)
        
        update_sql += ' WHERE id = %s'
        update_params.append(teacher_id)
        
        cursor.execute(update_sql, update_params)
        conn.commit()

        # 自动写入备注信息表
        if old_status and old_status != actual_target_status:
            _write_remark(teacher_id, teacher_name, old_status, actual_target_status)

        # 自动同步标签关系
        tag_sync_result = None
        if old_status and old_status != actual_target_status:
            try:
                tag_sync_result = _sync_tags_on_status_change(
                    cursor, teacher_id, teacher_name,
                    old_status, actual_target_status, transfer_direction
                )
                conn.commit()
            except Exception as e:
                logger.error(f"标签同步失败: {e}")
                try:
                    conn.rollback()
                except:
                    pass

        # 自动同步政治标签（共青团员、团籍、群众）
        political_tag_result = None
        if teacher_id_card:
            try:
                political_tag_result = _sync_political_tags(
                    cursor, teacher_id, teacher_id_card
                )
                conn.commit()
                if political_tag_result.get('added') or political_tag_result.get('removed'):
                    logger.info(
                        f"政治标签同步完成: {teacher_name}, "
                        f"新增={political_tag_result.get('added')}, "
                        f"移除={political_tag_result.get('removed')}"
                    )
            except Exception as e:
                logger.error(f"政治标签同步失败: {e}")
                try:
                    conn.rollback()
                except:
                    pass

        # 实时触发提醒已经在下面的循环中处理了
        # 后续主流程会正确匹配并创建待办，这里不需要重复处理
        
        # 检查是否需要党组织关系状态变更（调出、调离、去世、辞职）
        party_relation_result = None
        party_relation_trigger_statuses = ['调出', '调离', '去世', '辞职']
        if actual_target_status in party_relation_trigger_statuses and teacher_id_card:
            try:
                cursor.execute(
                    'SELECT id, name FROM "zao_yang_shi_tai_ping_zhen_zhong_xin_xue_xiao_dang_yuan_xin_xi_biao" WHERE id_card = %s',
                    (teacher_id_card,)
                )
                party_member = cursor.fetchone()
                if party_member:
                    party_relation_result = {
                        "requires_party_relation_update": True,
                        "teacher_name": teacher_name,
                        "teacher_id_card": teacher_id_card,
                        "party_member_id": party_member[0],
                        "party_member_name": party_member[1],
                        "new_employment_status": actual_target_status
                    }
            except Exception as e:
                logger.error(f"党员信息查询失败: {e}")
        
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
                    
                    # 查询最高学历信息（按学历代码降序，学历代码越大学历越高：1小学→8博士）
                    cursor.execute("""
                        SELECT education, graduate_date, graduate_school, major
                        FROM teacher_education_record
                        WHERE teacher_id = %s
                        ORDER BY education DESC
                        LIMIT 1
                    """, (teacher_id,))
                    education_row = cursor.fetchone()
                    
                    # 使用辅助函数构建完整数据
                    report_data = _build_retirement_report_data(cursor, teacher_id, teacher_row, id_card, education_row)
                    
                    # 安全获取值的辅助函数
                    def safe_get(key, default=None):
                        return report_data.get(key, default)
                    
                    # 检查是否已存在该教师的记录
                    cursor.execute("""
                        SELECT id FROM retirement_report_data WHERE teacher_id = %s
                    """, (teacher_id,))
                    existing_row = cursor.fetchone()
                    
                    # 所有退休呈报表字段及其数据来源
                    # 表字段名 -> report_data中的key
                    field_mapping = [
                        # 基础信息
                        ('姓名', '姓名'),
                        ('身份证号码', '身份证号码'),
                        ('性别', '性别'),
                        ('出生日期', '出生日期'),
                        ('民族', '民族'),
                        ('文化程度', '文化程度'),
                        ('参加工作时间', '参加工作时间'),
                        ('工作年限', '工作年限'),
                        ('籍贯', '籍贯'),
                        # 职务职称
                        ('职务', '职务'),
                        ('岗位', '岗位'),
                        ('技术职称', '技术职称'),
                        # 退休补充信息
                        ('现住址', '现住址'),
                        ('退休原因', '退休原因'),
                        ('退休后居住地址', '退休后居住地址'),
                        ('退休时间', '退休时间'),
                        ('是否独生子女', '是否独生子女'),
                        ('单位意见', '单位意见'),
                        ('证明人及其住址', '证明人及其住址'),
                        ('直系亲属供养情况', '直系亲属供养情况'),
                        ('直系亲属信息', '直系亲属信息'),
                        ('自何年何月', '自何年何月'),
                        ('至何年何月', '至何年何月'),
                        ('所在单位及职务', '所在单位及职务'),
                        ('入党年月', '入党年月'),
                        ('个人身份', '个人身份'),
                        ('个人编号', '个人编号'),
                        ('备注', '备注'),
                        # 工资信息
                        ('薪级工资', '薪级工资'),
                        ('岗位工资', '岗位工资'),
                        ('技术等级', '技术等级'),
                        ('最后一次职务升降时间', '最后一次职务升降时间'),
                        # 分类岗位字段（根据人员分类动态填充，9个岗位组）
                        # 时间点1: 管理岗位1 / 专技岗位2 / 工勤岗位3
                        ('事业管理岗位1', '事业管理岗位1'), ('薪级1', '薪级1'), ('对应原职务1', '对应原职务1'),
                        ('事业专技岗位2', '事业专技岗位2'), ('薪级2', '薪级2'), ('对应原职务2', '对应原职务2'),
                        ('事业工勤岗位3', '事业工勤岗位3'), ('薪级3', '薪级3'), ('对应技术等级3', '对应技术等级3'),
                        # 时间点2: 管理岗位4 / 专技岗位5 / 工勤岗位6
                        ('事业管理岗位4', '事业管理岗位4'), ('薪级4', '薪级4'), ('对应原职务4', '对应原职务4'),
                        ('事业专技岗位5', '事业专技岗位5'), ('薪级5', '薪级5'), ('对应原职务5', '对应原职务5'),
                        ('事业工勤岗位6', '事业工勤岗位6'), ('薪级6', '薪级6'), ('对应技术等级6', '对应技术等级6'),
                        # 时间点3: 管理岗位7 / 专技岗位8 / 工勤岗位9
                        ('退休时事业管理岗位7', '退休时事业管理岗位7'), ('薪级7', '薪级7'), ('对应原职务7', '对应原职务7'),
                        ('退休时事业专技岗位8', '退休时事业专技岗位8'), ('薪级8', '薪级8'), ('对应原职务8', '对应原职务8'),
                        ('退休时事业工勤岗位9', '退休时事业工勤岗位9'), ('薪级9', '薪级9'), ('对应技术等级9', '对应技术等级9'),
                    ]
                    
                    # 提取字段名和值
                    col_names = [m[0] for m in field_mapping]
                    col_values = [safe_get(m[1]) for m in field_mapping]
                    
                    if existing_row:
                        # UPDATE
                        set_clauses = [f'"{col}" = %s' for col in col_names]
                        update_sql = f"""
                            UPDATE retirement_report_data SET
                                {', '.join(set_clauses)},
                                updated_at = NOW()
                            WHERE teacher_id = %s
                        """
                        cursor.execute(update_sql, col_values + [teacher_id])
                    else:
                        # INSERT
                        quoted_cols = [f'"{col}"' for col in ['teacher_id'] + col_names]
                        placeholders = ['%s'] * (len(col_names) + 1)
                        insert_sql = f"""
                            INSERT INTO retirement_report_data (
                                {', '.join(quoted_cols)},
                                created_at, updated_at
                            ) VALUES ({', '.join(placeholders)}, NOW(), NOW())
                        """
                        cursor.execute(insert_sql, [teacher_id] + col_values)
                    
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
        logger.info(f"找到 {len(all_checklists)} 个有效清单模板, 目标状态: {actual_target_status}")
        
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
            logger.debug(f"  检查 {actual_target_status} 是否在 {target_statuses}: {actual_target_status in target_statuses}")
            if actual_target_status in target_statuses:
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
            
            response_data = {
                "status": "no_checklist",
                "message": f"当前任职状态 '{actual_target_status}' 下没有待办任务清单",
                "teacher_id": teacher_id,
                "new_status": actual_target_status,
                "created_checklists": []
            }
            if tag_sync_result:
                response_data["tag_sync"] = tag_sync_result
            if party_relation_result:
                response_data.update(party_relation_result)
            return response_data
        
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
                    f"状态变更触发: {actual_target_status}",
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
            "new_status": actual_target_status,
            "created_checklists": created_checklists
        }
        
        # 添加标签同步结果
        if tag_sync_result:
            response_data["tag_sync"] = tag_sync_result
        
        # 添加党组织关系状态变更信息
        if party_relation_result:
            response_data.update(party_relation_result)
        
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
