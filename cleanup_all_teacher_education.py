#!/usr/bin/env python3
"""
彻底清理教师学历记录的所有残留
"""
import json
import os

# 配置文件路径
CONFIG_DIR = 'd:/erp_thirteen/tp_education_system/backend/config'
TABLE_NAME_MAPPINGS_FILE = os.path.join(CONFIG_DIR, 'table_name_mappings.json')
MERGED_SCHEMA_FILE = os.path.join(CONFIG_DIR, 'merged_schema_mappings.json')
NAVIGATION_FILE = os.path.join(CONFIG_DIR, 'navigation.json')
FIELD_CONFIGS_DIR = os.path.join(CONFIG_DIR, 'field_configs')

print("=" * 80)
print("开始彻底清理教师学历记录的所有残留")
print("=" * 80)

# 1. 清理 merged_schema_mappings.json
print("\n【1. 清理 merged_schema_mappings.json】")
with open(MERGED_SCHEMA_FILE, 'r', encoding='utf-8') as f:
    schema_config = json.load(f)

# 删除 teacher_education_record 和 teacher_education_log
tables_to_delete = ['teacher_education_record', 'teacher_education_log']
deleted_count = 0

for table_name in tables_to_delete:
    if table_name in schema_config.get('tables', {}):
        del schema_config['tables'][table_name]
        print(f"  已删除表结构: {table_name}")
        deleted_count += 1
    
    # 删除相关字段映射
    if 'mappings' in schema_config:
        keys_to_delete = []
        for key, value in schema_config['mappings'].items():
            if isinstance(value, dict):
                if value.get('target_table') == table_name:
                    keys_to_delete.append(key)
            elif isinstance(value, str) and value == table_name:
                keys_to_delete.append(key)
        
        for key in keys_to_delete:
            del schema_config['mappings'][key]
            print(f"  已删除字段映射: {key}")

with open(MERGED_SCHEMA_FILE, 'w', encoding='utf-8') as f:
    json.dump(schema_config, f, ensure_ascii=False, indent=2)
print(f"  共删除 {deleted_count} 个表结构")

# 2. 清理 navigation.json
print("\n【2. 清理 navigation.json】")
with open(NAVIGATION_FILE, 'r', encoding='utf-8') as f:
    navigation = json.load(f)

def remove_from_navigation(modules):
    """递归删除导航中的教师学历记录"""
    for module in modules:
        if 'children' in module:
            original_count = len(module['children'])
            module['children'] = [
                child for child in module['children']
                if child.get('table_name') not in tables_to_delete
                and 'teacher_education' not in child.get('table_name', '')
            ]
            removed = original_count - len(module['children'])
            if removed > 0:
                print(f"  已从 {module.get('title', '未知模块')} 删除 {removed} 个节点")
            
            # 递归处理子节点
            remove_from_navigation(module['children'])

remove_from_navigation(navigation.get('modules', []))

with open(NAVIGATION_FILE, 'w', encoding='utf-8') as f:
    json.dump(navigation, f, ensure_ascii=False, indent=2