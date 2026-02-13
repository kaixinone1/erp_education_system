#!/usr/bin/env python3
"""
独立测试环境 - 验证占位符模板引擎
"""
import sys
import os
import re
import psycopg2

# 添加后端路径
sys.path.insert(0, r'd:\erp_thirteen\tp_education_system\backend')

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

def test_engine():
    """测试模板引擎"""
    print("=" * 70)
    print("独立测试 - 占位符模板引擎")
    print("=" * 70)
    
    engine = PlaceholderTemplateEngine(get_db_connection)
    template_id = "职工退休申报表html"
    
    # 测试1: 检查数据库数据
    print("\n【测试1】数据库中的教师数据")
    conn = get_db_connection()
    cursor = conn.cursor()
    
    for teacher_id in [273, 299]:
        cursor.execute('SELECT teacher_id, "姓名" FROM retirement_report_data WHERE teacher_id = %s', (teacher_id,))
        row = cursor.fetchone()
        if row:
            print(f"   教师ID {row[0]}: 姓名 = {row[1]}")
    
    cursor.close()
    conn.close()
    
    # 测试2: 检查模板文件
    print("\n【测试2】模板文件检查")
    template_path = r'd:\erp_thirteen\tp_education_system\backend\templates\职工退休申报表html.html'
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否有{{姓名}}
    name_placeholders = re.findall(r'\{\{\s*姓名\s*\}\}', content)
    print(f"   {{姓名}} 占位符: {len(name_placeholders)} 个")
    
    # 检查硬编码
    if '王德' in content:
        print(f"   ✗ 发现硬编码'王德': {content.count('王德')} 次")
    else:
        print(f"   ✓ 无硬编码'王德'")
    
    # 测试3: 生成文档
    print("\n【测试3】生成文档测试")
    for teacher_id in [273, 299]:
        html = engine.generate_document(template_id, teacher_id)
        
        # 查找姓名
        if '王军峰' in html:
            found_name = '王军峰'
        elif '王德' in html:
            found_name = '王德'
        else:
            found_name = '未找到'
        
        # 检查剩余占位符
        remaining = re.findall(r'\{\{\s*姓名\s*\}\}', html)
        
        print(f"   教师ID {teacher_id}: 生成姓名 = {found_name}, 剩余占位符 = {len(remaining)}")
    
    # 测试4: 直接测试get_data_from_table
    print("\n【测试4】数据获取方法测试")
    for teacher_id in [273, 299]:
        name = engine.get_data_from_table('retirement_report_data', '姓名', teacher_id)
        print(f"   教师ID {teacher_id}: get_data_from_table返回 = {name}")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    test_engine()
