#!/usr/bin/env python3
"""
清理 teacher_log 相关的所有配置
"""

import json
import os

CONFIG_DIR = r'd:\erp_thirteen\tp_education_system\backend\config'

def clean_merged_schema_mappings():
    """清理 merged_schema_mappings.json"""
    file_path = os.path.join(CONFIG_DIR, 'merged_schema_mappings.json')
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 删除 teacher_log 表定义
    if 'tables' in data and 'teacher_log' in data['tables']:
        del data['tables']['teacher_log']
        print("✅ 从 tables 中删除 teacher_log")
    
    # 删除 teacher_log 的字段映射 (在 mappings 列表中)
    if 'mappings' in data and isinstance(data['mappings'], list):
        original_count = len(data['mappings'])
        data['mappings'] = [m for m in data['mappings'] if isinstance(m, dict) and m.get('table') != 'teacher_log']
        removed_count = original_count - len(data['mappings'])
        if removed_count > 0:
            print(f"✅ 从 mappings 中删除 {removed_count} 个 teacher_log 相关映射")
    
    # 删除 relationships 中的 teacher_log
    if 'relationships' in data and 'teacher_basic' in data['relationships']:
        if 'children' in data['relationships']['teacher_basic']:
            if 'teacher_log' in data['relationships']['teacher_basic']['children']:
                data['relationships']['teacher_basic']['children'].remove('teacher_log')
                print("✅ 从 relationships.teacher_basic.children 中删除 teacher_log")
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("✅ merged_schema_mappings.json 已更新")

def clean_field_mappings():
    """清理 field_mappings.json"""
    file_path = os.path.join(CONFIG_DIR, 'field_mappings.json')
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 删除 teacher_log 的字段映射 (注意：顶层键是 'configs' 而不是 'mappings')
    target_key = None
    for key in ['configs', 'mappings']:
        if key in data and isinstance(data[key], list):
            target_key = key
            break
    
    if target_key:
        original_count = len(data[target_key])
        data[target_key] = [m for m in data[target_key] if isinstance(m, dict) and m.get('table') != 'teacher_log']
        removed_count = original_count - len(data[target_key])
        if removed_count > 0:
            print(f"✅ 从 {target_key} 中删除 {removed_count} 个 teacher_log 相关映射")
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("✅ field_mappings.json 已更新")

def clean_table_schemas():
    """清理 table_schemas.json"""
    file_path = os.path.join(CONFIG_DIR, 'table_schemas.json')
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 删除 teacher_log 表结构
    if 'tables' in data and 'teacher_log' in data['tables']:
        del data['tables']['teacher_log']
        print("✅ 从 tables 中删除 teacher_log")
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("✅ table_schemas.json 已更新")

if __name__ == "__main__":
    print("=" * 80)
    print("清理 teacher_log 相关配置")
    print("=" * 80)
    
    clean_merged_schema_mappings()
    clean_field_mappings()
    clean_table_schemas()
    
    print("\n" + "=" * 80)
    print("清理完成！")
    print("=" * 80)
