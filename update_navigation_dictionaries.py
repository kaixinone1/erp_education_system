import json
import shutil
from datetime import datetime

# 读取当前菜单
nav_file = 'd:/erp_thirteen/tp_education_system/backend/config/navigation.json'
with open(nav_file, 'r', encoding='utf-8') as f:
    nav = json.load(f)

# 备份当前菜单
backup_file = f'd:/erp_thirteen/tp_education_system/backend/config/navigation_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
shutil.copy(nav_file, backup_file)
print(f"已备份当前菜单到: {backup_file}")

# 找到字典管理模块
for module in nav['modules']:
    if module['id'] == 'system':
        for child in module['children']:
            if child['id'] == 'system-dictionaries':
                print(f"\n找到字典管理模块，当前有 {len(child['children'])} 个字典")
                
                # 要删除的字典表
                tables_to_remove = [
                    'dict_marital_status_dictionary',
                    'dict_nation_dictionary',
                    'dict_politics_status_dictionary',
                    'dict_teacher_status_dictionary'
                ]
                
                # 删除多出的字典表
                original_count = len(child['children'])
                child['children'] = [
                    item for item in child['children']
                    if item.get('table_name') not in tables_to_remove
                ]
                removed_count = original_count - len(child['children'])
                print(f"已删除 {removed_count} 个多出的字典表")
                
                # 要添加的字典表
                tables_to_add = [
                    {
                        "id": "table-dict_dictionary",
                        "title": "任职状态字典",
                        "name": "任职状态字典",
                        "icon": "Document",
                        "path": "/data/dict_dictionary",
                        "type": "component",
                        "component": "DynamicDataView",
                        "api_endpoint": "/api/data/dict_dictionary",
                        "table_name": "dict_dictionary",
                        "table_type": "dictionary"
                    },
                    {
                        "id": "table-dict_education_dictionary",
                        "title": "学历字典",
                        "name": "学历字典",
                        "icon": "Document",
                        "path": "/data/dict_education_dictionary",
                        "type": "component",
                        "component": "DynamicDataView",
                        "api_endpoint": "/api/data/dict_education_dictionary",
                        "table_name": "dict_education_dictionary",
                        "table_type": "dictionary"
                    },
                    {
                        "id": "table-dict_education_level_dictionary",
                        "title": "学历层次字典",
                        "name": "学历层次字典",
                        "icon": "Document",
                        "path": "/data/dict_education_level_dictionary",
                        "type": "component",
                        "component": "DynamicDataView",
                        "api_endpoint": "/api/data/dict_education_level_dictionary",
                        "table_name": "dict_education_level_dictionary",
                        "table_type": "dictionary"
                    }
                ]
                
                # 添加缺失的字典表
                child['children'].extend(tables_to_add)
                print(f"已添加 {len(tables_to_add)} 个缺失的字典表")
                
                print(f"\n现在字典管理模块有 {len(child['children'])} 个字典")
                
                # 显示最终的字典列表
                print("\n最终的字典列表：")
                for item in child['children']:
                    print(f"  - {item.get('title')} ({item.get('table_name')})")
                
                break

# 保存修改后的菜单
with open(nav_file, 'w', encoding='utf-8') as f:
    json.dump(nav, f, ensure_ascii=False, indent=2)

print(f"\n菜单已更新并保存到: {nav_file}")
