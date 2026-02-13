#!/usr/bin/env python3
"""
修复导入问题，清理不一致的表状态
"""

import psycopg2
import json
import os

DB_PARAMS = {
    'host': 'localhost',
    'database': 'taiping_education',
    'user': 'taiping_user',
    'password': 'taiping_password'
}

def fix_import():
    print("修复导入问题...")
    
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cursor = conn.cursor()
        
        # 1. 删除 teacher_record 表（如果存在）
        cursor.execute("DROP TABLE IF EXISTS teacher_record CASCADE")
        print("✓ 删除 teacher_record 表")
        
        # 2. 清理表名映射文件
        config_dir = r'd:\erp_thirteen\tp_education_system\backend\config'
        mapping_file = os.path.join(config_dir, 'table_name_mappings.json')
        
        if os.path.exists(mapping_file):
            with open(mapping_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 删除教师学历记录的映射
            if '教师学历记录' in data.get('mappings', {}):
                del data['mappings']['教师学历记录']
                print("✓ 删除 教师学历记录 的映射")
            
            # 清理反向映射
            reverse_mappings = data.get('reverse_mappings', {})
            keys_to_remove = [k for k, v in reverse_mappings.items() if v == '教师学历记录']
            for key in keys_to_remove:
                del data['reverse_mappings'][key]
                print(f"✓ 删除反向映射: {key}")
            
            with open(mapping_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print("✓ 更新表名映射文件")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("\n修复完成！")
        
    except Exception as e:
        print(f"错误: {e}")

if __name__ == "__main__":
    fix_import()
