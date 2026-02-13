#!/usr/bin/env python3
"""测试数据库连接 - 多次查询验证"""
import sys
sys.path.insert(0, r'd:\erp_thirteen\tp_education_system\backend')

import psycopg2
from services.placeholder_template_engine import PlaceholderTemplateEngine

DATABASE_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "database": "taiping_education",
    "user": "taiping_user",
    "password": "taiping_password"
}

def get_db_connection():
    return psycopg2.connect(**DATABASE_CONFIG)

print("=" * 70)
print("数据库连接测试 - 多次查询")
print("=" * 70)

engine = PlaceholderTemplateEngine(get_db_connection)

# 连续测试多次，看是否有缓存问题
for i in range(3):
    print(f"\n【第 {i+1} 轮测试】")
    for teacher_id in [273, 299]:
        name = engine.get_data_from_table('retirement_report_data', '姓名', teacher_id)
        print(f"   教师ID {teacher_id}: {name}")

# 测试生成文档
print("\n【文档生成测试 - 多次】")
for i in range(3):
    print(f"\n第 {i+1} 次生成:")
    for teacher_id in [273, 299]:
        html = engine.generate_document('职工退休申报表html', teacher_id)
        if '王军峰' in html:
            name = '王军峰'
        elif '王德' in html:
            name = '王德'
        else:
            name = '未找到'
        print(f"   教师ID {teacher_id}: {name}")

print("\n" + "=" * 70)
