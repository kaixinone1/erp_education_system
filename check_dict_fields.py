import json

# 读取配置文件
config_file = 'd:/erp_thirteen/tp_education_system/backend/config/merged_schema_mappings.json'

with open(config_file, 'r', encoding='utf-8') as f:
    config = json.load(f)

tables = config.get('tables', {})

# 检查 dict_dictionary 表的字段配置
if 'dict_dictionary' in tables:
    print('dict_dictionary (任职状态字典) 表配置:')
    table_config = tables['dict_dictionary']
    print(f'  chinese_name: {table_config.get("chinese_name")}')
    fields = table_config.get('fields', [])
    print(f'  字段数: {len(fields)}')
    if fields:
        print('  所有字段:')
        for f in fields:
            print(f'    {f.get("targetField")} -> {f.get("sourceField")}')
else:
    print('dict_dictionary 表不在配置中')
