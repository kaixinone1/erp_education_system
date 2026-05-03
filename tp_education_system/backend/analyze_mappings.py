import json
with open('config/field_mappings.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print('field_mappings.json 中所有表及其字段映射:')
print('='*60)

for config in data.get('configs', []):
    table_name = config.get('table_name')
    print(f'\n表名: {table_name}')
    print('-'*40)

    field_mappings = config.get('field_mappings', [])
    for fm in field_mappings[:5]:  # 只显示前5个
        print(f"  sourceField: {fm.get('sourceField')}")
        print(f"  targetField: {fm.get('targetField')}")
        print()

    if len(field_mappings) > 5:
        print(f'  ... 共 {len(field_mappings)} 个字段')