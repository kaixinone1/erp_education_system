#!/usr/bin/env python3
"""
修复导入问题 - 清理表名映射
"""

import json
import os

config_dir = r'd:\erp_thirteen\tp_education_system\backend\config'
mapping_file = os.path.join(config_dir, 'table_name_mappings.json')

if os.path.exists(mapping_file):
    with open(mapping_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("当前表名映射:")
    print(json.dumps(data, ensure_ascii=False, indent=2))
    
    # 删除教师学历记录的映射
    if '教师学历记录' in data.get('mappings', {}):
        del data['mappings']['教师学历记录']
        print("\n✓ 删除 教师学历记录 的映射")
    
    # 清理反向映射
    if 'teacher_record' in data.get('reverse_mappings', {}):
        del data['reverse_mappings']['teacher_record']
        print("✓ 删除 teacher_record 的反向映射")
    
    with open(mapping_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print("\n更新后的表名映射:")
    print(json.dumps(data, ensure_ascii=False, indent=2))
else:
    print("映射文件不存在")
