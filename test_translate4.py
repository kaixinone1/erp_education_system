"""
测试翻译功能
"""
import sys
sys.path.insert(0, 'd:/erp_thirteen/tp_education_system/backend')

from utils.name_translator import chinese_to_english

test_names = [
    "教师去世业务数据",
    "教师基础信息",
    "退休呈报数据",
    "退休呈报表",
    "教师工作业务数据",
    "教师专业技术资格",
    "教师学历记录",
    "教师工作变动情况",
    "事业单位养老保险",
    "机关事业单位养老保险改革过渡期内职务升降退休人员信息申报表"
]

for name in test_names:
    result = chinese_to_english(name)
    print(f"{name} -> {result}")
