#!/usr/bin/env python3
"""测试字典关联配置"""
import json
import os

CONFIG_DIR = 'd:/erp_thirteen/tp_education_system/backend/config'
SCHEMA_FILE = os.path.join(CONFIG_DIR, 'merged_schema_mappings.json')

def read_json_file(file_path):
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"读取文件失败: {e}")
    return None

# 读取配置
schema_config = read_json_file(SCHEMA_FILE)
table_schema = schema_config.get("tables", {}).get("teacher_education_record", {})
fields_config = table_schema.get("fields", [])

print("教师学历记录表的字段配置:")
for field_config in fields_config:
    target_field = field_config.get("targetField") or field_config.get("english_name")
    relation_type = field_config.get("relation_type")
    relation_table = field_config.get("relation_table")
    print(f"  - {target_field}: relation_type={relation_type}, relation_table={relation_table}")

# 模拟数据库列名
columns = ['id', 'name', 'id_card', 'education_type', 'education', 'degree', 'graduate_school', 'major', 'graduate_date', 'created_at', 'updated_at']

print("\n检查哪些字段在columns中:")
for field_config in fields_config:
    target_field = field_config.get("targetField") or field_config.get("english_name")
    if target_field in columns:
        print(f"  ✓ {target_field} 在 columns 中")
    else:
        print(f"  ✗ {target_field} 不在 columns 中")
