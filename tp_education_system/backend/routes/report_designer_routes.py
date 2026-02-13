"""
报表设计器API - 支持多表数据关联和精确报表生成
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, Optional
from datetime import datetime
import psycopg2
import sys
import os

# 添加 utils 目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.dict_utils import get_education_name

router = APIRouter(prefix="/api/report-designer", tags=["report-designer"])

DATABASE_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "database": "taiping_education",
    "user": "taiping_user",
    "password": "taiping_password"
}


def get_db_connection():
    return psycopg2.connect(**DATABASE_CONFIG)


def extract_gender_from_id_card(id_card: str) -> str:
    """从身份证号提取性别"""
    if not id_card or len(id_card) != 18:
        return ""
    try:
        gender_code = int(id_card[16])
        return "男" if gender_code % 2 == 1 else "女"
    except:
        return ""


def calculate_age(birth_date: str) -> int:
    """计算年龄"""
    if not birth_date:
        return 0
    try:
        birth = datetime.strptime(str(birth_date), "%Y-%m-%d")
        today = datetime.now()
        age = today.year - birth.year
        if (today.month, today.day) < (birth.month, birth.day):
            age -= 1
        return age
    except:
        return 0


def calculate_work_years(work_start_date: str) -> int:
    """计算工作年限"""
    if not work_start_date:
        return 0
    try:
        start = datetime.strptime(str(work_start_date), "%Y-%m-%d")
        today = datetime.now()
        years = today.year - start.year
        if (today.month, today.day) < (start.month, start.day):
            years -= 1
        return years
    except:
        return 0


def calculate_retirement_date(birth_date: str, gender: str) -> str:
    """计算退休日期"""
    if not birth_date or not gender:
        return ""
    try:
        birth = datetime.strptime(str(birth_date), "%Y-%m-%d")
        retirement_age = 60 if gender == "男" else 55
        retirement_year = birth.year + retirement_age
        return f"{retirement_year}-{birth.month:02d}-{birth.day:02d}"
    except:
        return ""


@router.get("/teacher-full-data")
async def get_teacher_full_data(teacher_id: int = Query(..., description="教师ID")):
    """
    获取教师完整数据（多表关联）
    优先从 retirement_report_form 表获取，如果没有则从其他表收集
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 1. 首先尝试从 retirement_report_form 表获取数据
        cursor.execute("""
            SELECT teacher_id, teacher_name, gender, birth_date, id_card, ethnicity,
                   native_place, education, graduation_school, major, degree,
                   work_start_date, work_unit, position, title, age, work_years,
                   retirement_date, contact_phone, is_only_child, join_party_date,
                   current_address, work_experience, retirement_reason, family_members,
                   retirement_address, pension_unit
            FROM retirement_report_form
            WHERE teacher_id = %s
            ORDER BY updated_at DESC
            LIMIT 1
        """, (teacher_id,))

        report_row = cursor.fetchone()

        if report_row:
            # 从 retirement_report_form 表构建数据
            full_data = {
                "teacher_id": report_row[0],
                "teacher_name": report_row[1] or "",
                "gender": report_row[2] or "",
                "birth_date": str(report_row[3]) if report_row[3] else "",
                "id_card": report_row[4] or "",
                "ethnicity": report_row[5] or "",
                "native_place": report_row[6] or "",
                "education": report_row[7] or "",
                "graduation_school": report_row[8] or "",
                "major": report_row[9] or "",
                "degree": report_row[10] or "",
                "work_start_date": str(report_row[11]) if report_row[11] else "",
                "work_unit": report_row[12] or "枣阳市太平镇中心学校",
                "position": report_row[13] or "",
                "title": report_row[14] or "",
                "age": report_row[15] or 0,
                "work_years": report_row[16] or 0,
                "retirement_date": str(report_row[17]) if report_row[17] else "",
                "contact_phone": report_row[18] or "",
                "is_only_child": report_row[19] or "",
                "join_party_date": report_row[20] or "",
                "current_address": report_row[21] or "",
                "work_experience": report_row[22] if report_row[22] else [],
                "retirement_reason": report_row[23] or "",
                "family_members": report_row[24] or "",
                "retirement_address": report_row[25] or "",
                "pension_unit": report_row[26] or "枣阳市人力资源和社会保障局"
            }
        else:
            # 2. 从其他表收集数据
            # 获取基本信息
            cursor.execute("""
                SELECT id, name, id_card, archive_birth_date, ethnicity,
                       native_place, work_start_date, contact_phone
                FROM teacher_basic_info
                WHERE id = %s
            """, (teacher_id,))

            basic_row = cursor.fetchone()
            if not basic_row:
                raise HTTPException(status_code=404, detail="教师不存在")

            # 获取最高教育经历（通过 teacher_id 关联）
            cursor.execute("""
                SELECT education, graduate_school, major, degree
                FROM teacher_education_record
                WHERE teacher_id = %s
                ORDER BY graduate_date DESC
                LIMIT 1
            """, (teacher_id,))

            edu_row = cursor.fetchone()

            # 构建完整数据
            birth_date = basic_row[3]
            id_card = basic_row[2]
            gender = extract_gender_from_id_card(id_card)

            # 格式化日期
            birth_date_str = str(birth_date) if birth_date else ""
            birth_year = birth_date.year if birth_date else ""
            birth_month = birth_date.month if birth_date else ""

            work_start_date = basic_row[6]
            work_start_str = str(work_start_date) if work_start_date else ""

            full_data = {
                "teacher_id": basic_row[0],
                "teacher_name": basic_row[1] or "",
                "id_card": id_card or "",
                "birth_date": birth_date_str,
                "birth_year": birth_year,
                "birth_month": birth_month,
                "gender": gender,
                "ethnicity": basic_row[4] or "",  # 民族
                "native_place": basic_row[5] or "",  # 籍贯
                "work_start_date": work_start_str,
                "contact_phone": basic_row[7] or "",

                # 教育信息
                "education": get_education_name(edu_row[0], DATABASE_CONFIG) if edu_row else "",  # 文化程度 - 转换为中文
                "graduation_school": edu_row[1] if edu_row else "",
                "major": edu_row[2] if edu_row else "",
                "degree": edu_row[3] if edu_row else "",

                # 工作信息
                "work_unit": "枣阳市太平镇中心学校",
                "position": "",  # 职务
                "title": "",  # 技术职称

                # 计算字段
                "age": calculate_age(birth_date),
                "work_years": calculate_work_years(work_start_date),
                "retirement_date": calculate_retirement_date(birth_date, gender),

                # 缺失字段（需要用户填写）
                "is_only_child": "",  # 是否独生子女
                "join_party_date": "",  # 入党年月
                "current_address": "",  # 现在住址
                "work_experience": [],  # 工作简历
                "retirement_reason": "",  # 退休原因
                "family_members": "",  # 供养直系亲属
                "retirement_address": "",  # 退休后居住地址
                "pension_unit": "枣阳市人力资源和社会保障局"  # 发给退休费的单位
            }

        cursor.close()
        conn.close()

        return {
            "status": "success",
            "data": full_data
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取教师数据失败: {str(e)}")
