#!/usr/bin/env python3
"""
退休日期和工作年限计算器
根据人社部发【2024】94号文件规定计算
"""
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from typing import Optional, Tuple


def calculate_original_retirement_date(birth_date: date, gender: str, personal_identity: str = "干部") -> date:
    """
    计算原法定退休年龄
    
    Args:
        birth_date: 出生日期
        gender: 性别（男/女）
        personal_identity: 个人身份（干部/工勤）
    
    Returns:
        原退休日期
    """
    if gender == "男":
        # 男性统一60岁退休
        return birth_date + relativedelta(years=60)
    elif gender == "女":
        if personal_identity == "干部":
            # 女性干部55岁退休
            return birth_date + relativedelta(years=55)
        else:
            # 女性工人50岁退休
            return birth_date + relativedelta(years=50)
    else:
        # 默认60岁
        return birth_date + relativedelta(years=60)


def calculate_delay_months(birth_date: date, gender: str, personal_identity: str, original_retirement_date: date) -> int:
    """
    计算延迟月数
    
    根据人社部发【2024】94号文件规定：
    - 男性：1965年1月-1976年8月出生，每4个月延迟1个月，最多36个月
    - 女性干部：1970年1月-1981年8月出生，每4个月延迟1个月，最多36个月
    - 女性工人：1975年1月-1984年10月出生，每2个月延迟1个月，最多60个月
    
    Args:
        birth_date: 出生日期
        gender: 性别（男/女）
        personal_identity: 个人身份（干部/工勤）
        original_retirement_date: 原退休日期
    
    Returns:
        延迟月数
    """
    # 基准日期：2025年1月1日
    base_date = date(2025, 1, 1)
    
    if gender == "男":
        # 男性：1976年9月1日前出生的适用延迟规则
        if birth_date < date(1976, 9, 1):
            # 计算从2025年1月到原退休日期的月数
            months_diff = (original_retirement_date.year - base_date.year) * 12 + \
                         (original_retirement_date.month - base_date.month)
            # 每4个月延迟1个月
            delay_months = int(months_diff / 4 + 1)
            # 最多延迟36个月
            return min(delay_months, 36)
        else:
            # 1976年9月1日后出生的，直接延迟36个月
            return 36
            
    elif gender == "女":
        if personal_identity == "干部":
            # 女性干部：1981年9月1日前出生的适用延迟规则
            if birth_date < date(1981, 9, 1):
                months_diff = (original_retirement_date.year - base_date.year) * 12 + \
                             (original_retirement_date.month - base_date.month)
                delay_months = int(months_diff / 4 + 1)
                return min(delay_months, 36)
            else:
                return 36
        else:
            # 女性工人：1984年11月1日前出生的适用延迟规则
            if birth_date < date(1984, 11, 1):
                months_diff = (original_retirement_date.year - base_date.year) * 12 + \
                             (original_retirement_date.month - base_date.month)
                # 每2个月延迟1个月
                delay_months = int(months_diff / 2 + 1)
                return min(delay_months, 60)
            else:
                return 60
    
    return 0


def calculate_actual_retirement_date(original_retirement_date: date, delay_months: int) -> date:
    """
    计算现退休日期
    
    Args:
        original_retirement_date: 原退休日期
        delay_months: 延迟月数
    
    Returns:
        现退休日期
    """
    return original_retirement_date + relativedelta(months=delay_months)


def calculate_work_years(work_start_date: date, retirement_date: date) -> int:
    """
    计算工作年限
    
    Args:
        work_start_date: 参加工作时间
        retirement_date: 退休日期
    
    Returns:
        工作年限（年）
    """
    years = retirement_date.year - work_start_date.year
    if (retirement_date.month, retirement_date.day) < (work_start_date.month, work_start_date.day):
        years -= 1
    return max(0, years)


def calculate_retirement_info(
    birth_date: date,
    gender: str,
    personal_identity: str,
    work_start_date: date,
    custom_retirement_date: Optional[date] = None
) -> dict:
    """
    计算退休相关信息
    
    Args:
        birth_date: 出生日期
        gender: 性别
        personal_identity: 个人身份
        work_start_date: 参加工作时间
        custom_retirement_date: 自定义退休日期（可选，用于提前/延后办理）
    
    Returns:
        包含退休信息的字典
    """
    # 计算原退休日期
    original_retirement_date = calculate_original_retirement_date(birth_date, gender, personal_identity)
    
    # 计算延迟月数
    delay_months = calculate_delay_months(birth_date, gender, personal_identity, original_retirement_date)
    
    # 计算现退休日期
    calculated_retirement_date = calculate_actual_retirement_date(original_retirement_date, delay_months)
    
    # 使用自定义退休日期（如果有）
    actual_retirement_date = custom_retirement_date if custom_retirement_date else calculated_retirement_date
    
    # 计算工作年限
    work_years = calculate_work_years(work_start_date, actual_retirement_date)
    
    return {
        "birth_date": birth_date,
        "gender": gender,
        "personal_identity": personal_identity,
        "work_start_date": work_start_date,
        "original_retirement_date": original_retirement_date,
        "delay_months": delay_months,
        "calculated_retirement_date": calculated_retirement_date,
        "actual_retirement_date": actual_retirement_date,
        "work_years": work_years
    }


# 测试函数
if __name__ == "__main__":
    # 测试用例1：男性，1965年6月7日出生，干部
    birth_date1 = date(1965, 6, 7)
    work_start_date1 = date(1985, 7, 1)
    result1 = calculate_retirement_info(birth_date1, "男", "干部", work_start_date1)
    print("测试用例1（男性，1965/6/7，干部）：")
    print(f"  原退休日期：{result1['original_retirement_date']}")
    print(f"  延迟月数：{result1['delay_months']}")
    print(f"  现退休日期：{result1['calculated_retirement_date']}")
    print(f"  工作年限：{result1['work_years']}年")
    print()
    
    # 测试用例2：女性干部，1970年10月15日出生
    birth_date2 = date(1970, 10, 15)
    work_start_date2 = date(1990, 8, 1)
    result2 = calculate_retirement_info(birth_date2, "女", "干部", work_start_date2)
    print("测试用例2（女性干部，1970/10/15）：")
    print(f"  原退休日期：{result2['original_retirement_date']}")
    print(f"  延迟月数：{result2['delay_months']}")
    print(f"  现退休日期：{result2['calculated_retirement_date']}")
    print(f"  工作年限：{result2['work_years']}年")
