import json
import os
from collections import defaultdict

# 读取所有映射文件
config_dir = 'd:\\erp_thirteen\\tp_education_system\\backend\\config'

# 1. 表名映射
table_name_mappings_file = os.path.join(config_dir, 'table_name_mappings.json')
with open(table_name_mappings_file, 'r', encoding='utf-8') as f:
    table_name_mappings = json.load(f)

# 2. 字段名映射
field_name_mappings_file = os.path.join(config_dir, 'field_name_mappings.json')
with open(field_name_mappings_file, 'r', encoding='utf-8') as f:
    field_name_mappings = json.load(f)

# 3. merged_schema_mappings
merged_schema_file = os.path.join(config_dir, 'merged_schema_mappings.json')
with open(merged_schema_file, 'r', encoding='utf-8') as f:
    merged_schema = json.load(f)

# 分析表名映射
print("=" * 80)
print("表名映射分析")
print("=" * 80)

table_mappings = table_name_mappings.get('mappings', {})
print(f"\n总共有 {len(table_mappings)} 个表名映射")

# 分析字段名映射
print("\n" + "=" * 80)
print("字段名映射分析")
print("=" * 80)

field_mappings = field_name_mappings.get('mappings', {})
reverse_field_mappings = field_name_mappings.get('reverse_mappings', {})

print(f"\n总共有 {len(field_mappings)} 个字段名映射")

# 检查翻译质量
print("\n" + "=" * 80)
print("翻译质量检查")
print("=" * 80)

# 检查字段名翻译质量
bad_translations = []
good_translations = []

for chinese, english in field_mappings.items():
    # 检查是否是无意义的翻译
    if english.startswith('field_') and english[6:].isdigit():
        bad_translations.append({
            'chinese': chinese,
            'english': english,
            'reason': '无意义序号字段名'
        })
    elif english.startswith('name_') and english[5:].isdigit():
        bad_translations.append({
            'chinese': chinese,
            'english': english,
            'reason': '无意义序号字段名'
        })
    elif len(english) < 3:
        bad_translations.append({
            'chinese': chinese,
            'english': english,
            'reason': '字段名过短'
        })
    else:
        good_translations.append({
            'chinese': chinese,
            'english': english
        })

print(f"\n翻译质量统计：")
print(f"  优质翻译：{len(good_translations)} 个")
print(f"  需要改进：{len(bad_translations)} 个")

if bad_translations:
    print(f"\n需要改进的字段名（前20个）：")
    for item in bad_translations[:20]:
        print(f"  {item['chinese']:30s} -> {item['english']:30s} ({item['reason']})")

# 从merged_schema中提取所有字段映射
print("\n" + "=" * 80)
print("从merged_schema提取字段映射")
print("=" * 80)

schema_field_mappings = defaultdict(dict)

for table_name, table_info in merged_schema.get('tables', {}).items():
    chinese_table_name = table_info.get('chinese_name', table_name)
    fields = table_info.get('fields', [])
    
    for field in fields:
        chinese_field = field.get('name') or field.get('chinese_name') or field.get('sourceField')
        english_field = field.get('name') or field.get('targetField') or field.get('english_name')
        
        if chinese_field and english_field:
            schema_field_mappings[table_name][chinese_field] = english_field

print(f"\n从 {len(schema_field_mappings)} 个表中提取了字段映射")

# 检查schema中的字段名翻译质量
schema_bad_translations = []

for table_name, fields in schema_field_mappings.items():
    for chinese, english in fields.items():
        if english.startswith('field_') and english[6:].isdigit():
            schema_bad_translations.append({
                'table': table_name,
                'chinese': chinese,
                'english': english,
                'reason': '无意义序号字段名'
            })
        elif english.startswith('name_') and english[5:].isdigit():
            schema_bad_translations.append({
                'table': table_name,
                'chinese': chinese,
                'english': english,
                'reason': '无意义序号字段名'
            })

print(f"\nschema中需要改进的字段名：{len(schema_bad_translations)} 个")
if schema_bad_translations:
    print(f"\n示例（前10个）：")
    for item in schema_bad_translations[:10]:
        print(f"  {item['table']:30s} | {item['chinese']:30s} -> {item['english']:30s}")

# 保存分析结果
result = {
    'table_mappings': table_mappings,
    'field_mappings': field_mappings,
    'good_translations': good_translations,
    'bad_translations': bad_translations,
    'schema_bad_translations': schema_bad_translations
}

with open('d:\\erp_thirteen\\translation_analysis.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(f"\n分析结果已保存到：d:\\erp_thirteen\\translation_analysis.json")
