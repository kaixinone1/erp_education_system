#!/usr/bin/env python3
"""
修复系统字段的中文名
"""
import json
import os
import psycopg2

DATABASE_CONFIG = {
    'host': 'localhost',
    'port': '5432',
    'database': 'taiping_education',
    'user': 'taiping_user',
    'password': 'taiping_password'
}

SCHEMA_FILE = r'd:\erp_thirteen\tp_education_system\backend\config\merged_schema_mappings.json'

# 系统字段中文映射
SYSTEM_FIELD_NAMES = {
    'id': '记录编号',
    'teacher_id': '教师编号',
    'template_id': '模板编号',
    'created_at': '创建时间',
    'updated_at': '更新时间'
}

def update_schema_config():
    # 读取配置文件
    with open(SCHEMA_FILE, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # 获取 retirement_report_data 表的字段
    table = config['tables'].get('retirement_report_data')
    if not table:
        print("未找到 retirement_report_data 表配置")
        return
    
    # 更新字段中文名
    for field in table.get('fields', []):
        field_name = field.get('targetField') or field.get('english_name', '')
        if field_name in SYSTEM_FIELD_NAMES:
            # 更新系统字段的中文名
            field['sourceField'] = SYSTEM_FIELD_NAMES[field_name]
            field['chinese_name'] = SYSTEM_FIELD_NAMES[field_name]
            print(f"更新字段: {field_name} -> {SYSTEM_FIELD_NAMES[field_name]}")
    
    # 保存配置文件
    with open(SCHEMA_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    
    print("\n配置文件已更新！")

if __name__ == '__main__':
    update_schema_config()
