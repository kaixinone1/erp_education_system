#!/usr/bin/env python3
"""
清理配置文件中的重复表配置
"""

import json
import os

CONFIG_DIR = r'd:\erp_thirteen\tp_education_system\backend\config'

def clean_merged_schema_mappings():
    """清理 merged_schema_mappings.json"""
    file_path = os.path.join(CONFIG_DIR, 'merged_schema_mappings.json')
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 要删除的表
        tables_to_remove = ['teacher_archive', 'teacher_history', 'teacher_log']
        
        # 清理 tables
        for table_name in tables_to_remove:
            if table_name in data.get('tables', {}):
                del data['tables'][table_name]
                print(f"✓ 从 tables 中移除: {table_name}")
        
        # 清理 mappings
        original_mappings_count = len(data.get('mappings', []))
        data['mappings'] = [
            m for m in data.get('mappings', []) 
            if m.get('table') not in tables_to_remove
        ]
        removed_mappings = original_mappings_count - len(data['mappings'])
        if removed_mappings > 0:
            print(f"✓ 从 mappings 中移除 {removed_mappings} 条记录")
        
        # 清理 relationships
        for table_name in tables_to_remove:
            if table_name in data.get('relationships', {}):
                del data['relationships'][table_name]
                print(f"✓ 从 relationships 中移除: {table_name}")
        
        # 保存文件
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"\n✓ merged_schema_mappings.json 清理完成")
        
    except Exception as e:
        print(f"✗ 清理 merged_schema_mappings.json 失败: {e}")

def clean_table_schemas():
    """清理 table_schemas.json"""
    file_path = os.path.join(CONFIG_DIR, 'table_schemas.json')
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 要删除的表
        tables_to_remove = ['teacher_archive', 'teacher_history', 'teacher_log']
        
        # 清理 tables
        for table_name in tables_to_remove:
            if table_name in data.get('tables', {}):
                del data['tables'][table_name]
                print(f"✓ 从 table_schemas 中移除: {table_name}")
        
        # 保存文件
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"\n✓ table_schemas.json 清理完成")
        
    except Exception as e:
        print(f"✗ 清理 table_schemas.json 失败: {e}")

def clean_field_mappings():
    """清理 field_mappings.json"""
    file_path = os.path.join(CONFIG_DIR, 'field_mappings.json')
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 要删除的表
        tables_to_remove = ['teacher_archive', 'teacher_history', 'teacher_log']
        
        # 清理 mappings
        original_count = len(data.get('mappings', []))
        data['mappings'] = [
            m for m in data.get('mappings', []) 
            if m.get('table') not in tables_to_remove
        ]
        removed = original_count - len(data['mappings'])
        
        if removed > 0:
            print(f"✓ 从 field_mappings 中移除 {removed} 条记录")
        
        # 保存文件
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"\n✓ field_mappings.json 清理完成")
        
    except Exception as e:
        print(f"✗ 清理 field_mappings.json 失败: {e}")

def clean_navigation():
    """清理 navigation.json"""
    file_path = os.path.join(CONFIG_DIR, 'navigation.json')
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 要删除的表
        tables_to_remove = ['teacher_archive', 'teacher_history', 'teacher_log']
        
        # 递归清理菜单项
        def clean_menu_items(items):
            cleaned = []
            for item in items:
                # 检查是否需要删除
                if item.get('table_name') in tables_to_remove:
                    print(f"✓ 从导航中移除: {item.get('title', item.get('id'))}")
                    continue
                
                # 递归清理子菜单
                if 'children' in item:
                    item['children'] = clean_menu_items(item['children'])
                
                cleaned.append(item)
            return cleaned
        
        data['modules'] = clean_menu_items(data.get('modules', []))
        
        # 保存文件
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"\n✓ navigation.json 清理完成")
        
    except Exception as e:
        print(f"✗ 清理 navigation.json 失败: {e}")

if __name__ == "__main__":
    print("开始清理配置文件...")
    print("=" * 60)
    
    clean_merged_schema_mappings()
    print()
    clean_table_schemas()
    print()
    clean_field_mappings()
    print()
    clean_navigation()
    
    print("=" * 60)
    print("配置文件清理完成！")
