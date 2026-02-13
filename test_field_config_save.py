#!/usr/bin/env python3
"""
测试新的字段配置保存机制
"""

import sys
sys.path.append(r'd:\erp_thirteen\tp_education_system\backend')

from core.field_config_manager import field_config_manager
from core.table_name_manager import TableNameManager

print("=" * 80)
print("测试字段配置保存机制")
print("=" * 80)

# 1. 测试保存字段配置
print("\n1. 测试保存字段配置")
test_config = {
    'config_name': '教师基础信息',
    'table_name': 'teacher_basic',
    'table_type': 'master',
    'source_file_pattern': '*教师基础信息*',
    'field_mappings': [
        {'sourceField': '姓名', 'targetField': 'name', 'dataType': 'VARCHAR'},
        {'sourceField': '性别', 'targetField': 'gender', 'dataType': 'VARCHAR'},
        {'sourceField': '年龄', 'targetField': 'age', 'dataType': 'INTEGER'}
    ]
}

result = field_config_manager.save_config(test_config)
print(f"  保存结果: {result}")

# 2. 测试重复保存（应该更新）
print("\n2. 测试重复保存（应该更新版本）")
test_config['field_mappings'].append({'sourceField': '电话', 'targetField': 'phone', 'dataType': 'VARCHAR'})
result = field_config_manager.save_config(test_config)
print(f"  更新结果: {result}")

# 3. 测试获取所有配置
print("\n3. 测试获取所有配置")
all_configs = field_config_manager.get_all_configs()
print(f"  共有 {len(all_configs)} 个配置")
for config in all_configs:
    print(f"    - {config['config_name']} (v{config.get('version', 1)})")

# 4. 测试根据名称获取配置
print("\n4. 测试根据名称获取配置")
config = field_config_manager.get_config_by_name('教师基础信息')
if config:
    print(f"  找到配置: {config['config_name']}")
    print(f"  表名: {config['table_name']}")
    print(f"  字段数: {len(config['field_mappings'])}")
    print(f"  版本: {config.get('version', 1)}")

# 5. 测试全局字段映射
print("\n5. 测试全局字段映射")
global_mappings = field_config_manager.get_global_mappings()
print(f"  全局字段映射数: {len(global_mappings)}")
for cn, en in list(global_mappings.items())[:5]:
    print(f"    {cn} -> {en}")

# 6. 测试文件名匹配
print("\n6. 测试文件名匹配")
matching = field_config_manager.find_matching_configs('教师基础信息.xlsx')
print(f"  匹配到 {len(matching)} 个配置")
for m in matching:
    print(f"    - {m['config_name']} (分数: {m.get('match_score', 0)})")

# 7. 测试 TableNameManager 同步
print("\n7. 测试 TableNameManager 同步")
table_manager = TableNameManager()
table_manager.register_table_name(
    '教师学历记录',
    'teacher_education_record',
    'master',
    [
        {'sourceField': '学校', 'targetField': 'school', 'dataType': 'VARCHAR'},
        {'sourceField': '专业', 'targetField': 'major', 'dataType': 'VARCHAR'}
    ]
)

# 8. 验证同步结果
print("\n8. 验证同步结果")
config = field_config_manager.get_config_by_name('教师学历记录')
if config:
    print(f"  TableNameManager 注册后，field_mappings.json 中已同步:")
    print(f"    配置名: {config['config_name']}")
    print(f"    表名: {config['table_name']}")

# 9. 测试反向同步
print("\n9. 测试从 field_mappings.json 同步到 table_name_mappings.json")
sync_count = table_manager.sync_from_field_mappings()
print(f"  同步了 {sync_count} 个表名映射")

print("\n" + "=" * 80)
print("测试完成!")
print("=" * 80)
