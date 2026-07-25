"""
目标名称映射配置
"""
from typing import Dict, Optional

TARGET_NAME_MAPPING = {
    # 内部表
    "retirement_report_form": "退休呈报表",
    "position_upgrade_form": "职务升级表",
    "performance_pay_summary": "绩效工资汇总",
    "retirement_certificate": "退休证",

    # 外部链接
    "http://zwfw.hubei.gov.cn/webview/fw/frfw.html": "湖北政务网",
    "https://admin.hblgj.gov.cn/IpWHRdyAcT.php/member?ref=addtabs": "湖北老干部网",

    # 其他
    "internal_table": "内部数据表",
    "external_link": "外部链接",
    "auto_summary": "自动汇总",
    "issue_certificate": "证件签发"
}

EMPLOYMENT_STATUS_OPTIONS = [
    {"value": "在职", "label": "在职"},
    {"value": "离休", "label": "离休"},
    {"value": "退休", "label": "退休"}
]

def get_target_display_name(target: str) -> str:
    """获取目标的中文显示名称"""
    if not target:
        return "未设置"

    # 如果是网址，直接显示
    if target.startswith("http://") or target.startswith("https://"):
        return target

    # 查表映射
    return TARGET_NAME_MAPPING.get(target, target)

def get_all_target_options() -> list:
    """获取所有目标选项"""
    return [
        {"value": "retirement_report_form", "label": "退休呈报表", "type": "内部表"},
        {"value": "position_upgrade_form", "label": "职务升级表", "type": "内部表"},
        {"value": "performance_pay_summary", "label": "绩效工资汇总", "type": "自动汇总"},
        {"value": "retirement_certificate", "label": "退休证", "type": "签发证件"},
        {"value": "http://zwfw.hubei.gov.cn/webview/fw/frfw.html", "label": "湖北政务网", "type": "外部链接"},
        {"value": "https://admin.hblgj.gov.cn/IpWHRdyAcT.php/member?ref=addtabs", "label": "湖北老干部网", "type": "外部链接"},
    ]

def get_employment_status_options() -> list:
    """获取任职状态选项"""
    return EMPLOYMENT_STATUS_OPTIONS
