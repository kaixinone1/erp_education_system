#!/usr/bin/env python3
"""
清理所有配置文件 - 重置为初始状态
"""

import os
import json
import shutil

CONFIG_DIR = r'd:\erp_thirteen\tp_education_system\backend\config'

print("=" * 80)
print("清理所有配置文件")
print("=" * 80)

# 1. 清理 table_name_mappings.json
print("\n1. 重置 table_name_mappings.json...")
table_name_mappings = {
    "mappings": {},
    "reverse_mappings": {}
}
with open(os.path.join(CONFIG_DIR, 'table_name_mappings.json'), 'w', encoding='utf-8') as f:
    json.dump(table_name_mappings, f, ensure_ascii=False, indent=2)
print("   ✓ 已重置")

# 2. 清理 navigation.json - 只保留基础菜单结构
print("\n2. 重置 navigation.json...")
navigation = {
    "modules": [
        {
            "id": "data-center",
            "title": "数据中心",
            "icon": "DataLine",
            "path": "/data-center",
            "type": "module",
            "children": [
                {
                    "id": "data-import",
                    "title": "数据导入",
                    "icon": "Upload",
                    "path": "/data-import",
                    "type": "component",
                    "component": "DataImport"
                },
                {
                    "id": "table-structure",
                    "title": "表结构管理",
                    "icon": "Setting",
                    "path": "/data/table-structure",
                    "type": "component",
                    "component": "TableStructure"
                },
                {
                    "id": "module-1770217750775",
                    "title": "数据清理",
                    "icon": "Setting",
                    "path": "/data-center/sub-1770217750775",
                    "type": "module",
                    "children": [
                        {
                            "id": "data-cleanup-tool",
                            "title": "数据清理工具",
                            "icon": "Delete",
                            "path": "/admin/data-cleanup",
                            "type": "component",
                            "component": "DataCleanupView"
                        }
                    ]
                }
            ]
        },
        {
            "id": "personnel",
            "title": "人事管理",
            "icon": "User",
            "path": "/personnel",
            "type": "module",
            "children": []
        }
    ]
}
with open(os.path.join(CONFIG_DIR, 'navigation.json'), 'w', encoding='utf-8') as f:
    json.dump(navigation, f, ensure_ascii=False, indent=2)
print("   ✓ 已重置")

# 3. 清理 field_configs 目录
print("\n3. 清理 field_configs 目录...")
field_configs_dir = os.path.join(CONFIG_DIR, 'field_configs')
if os.path.exists(field_configs_dir):
    # 删除所有json文件
    for filename in os.listdir(field_configs_dir):
        if filename.endswith('.json'):
            os.remove(os.path.join(field_configs_dir, filename))
            print(f"   ✓ 已删除: {filename}")
else:
    os.makedirs(field_configs_dir, exist_ok=True)
    print("   ✓ 目录已创建")

# 4. 重置其他配置文件
print("\n4. 重置其他配置文件...")
other_configs = {
    'merged_schema_mappings.json': {"tables": {}},
    'field_mappings.json': {},
    'table_schemas.json': {}
}

for filename, default_content in other_configs.items():
    filepath = os.path.join(CONFIG_DIR, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(default_content, f, ensure_ascii=False, indent=2)
    print(f"   ✓ 已重置: {filename}")

print("\n" + "=" * 80)
print("所有配置文件已清理完成！")
print("=" * 80)
