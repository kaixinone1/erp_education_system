#!/usr/bin/env python3
"""
批量更新配置文件中的 data_452489 为 teacher_basic
"""

import json
import os

def update_json_file(file_path, old_value, new_value):
    """更新JSON文件中的字符串"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 替换所有出现的 old_value
        new_content = content.replace(old_value, new_value)
        
        if content != new_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"✓ 已更新: {file_path}")
            return True
        else:
            print(f"  无需更新: {file_path}")
            return False
    except Exception as e:
        print(f"✗ 更新失败 {file_path}: {e}")
        return False

def main():
    config_dir = r'd:\erp_thirteen\tp_education_system\backend\config'
    
    files_to_update = [
        'merged_schema_mappings.json',
        'field_mappings.json',
        'table_schemas.json'
    ]
    
    print("开始更新配置文件...")
    print("=" * 60)
    
    updated_count = 0
    for filename in files_to_update:
        file_path = os.path.join(config_dir, filename)
        if os.path.exists(file_path):
            if update_json_file(file_path, 'data_452489', 'teacher_basic'):
                updated_count += 1
        else:
            print(f"✗ 文件不存在: {file_path}")
    
    print("=" * 60)
    print(f"更新完成，共更新 {updated_count} 个文件")

if __name__ == "__main__":
    main()
