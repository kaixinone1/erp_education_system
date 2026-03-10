import json

# 读取配置文件
config_file = 'd:/erp_thirteen/tp_education_system/backend/config/merged_schema_mappings.json'

with open(config_file, 'r', encoding='utf-8') as f:
    config = json.load(f)

tables = config.get('tables', {})

# 检查 teacher_basic_info 表的配置
if 'teacher_basic_info' in tables:
    print('teacher_basic_info 表配置:')
    table_config = tables['teacher_basic_info']
    print(f'  chinese_name: {table_config.get("chinese_name")}')
    fields = table_config.get('fields', [])
    print(f'  字段数: {len(fields)}')
    if fields:
        print('  前3个字段:')
        for f in fields[:3]:
            print(f'    {f}')
