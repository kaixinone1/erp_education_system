#!/usr/bin/env python3
"""
彻底调查教师学历记录表的所有残留信息
"""
import psycopg2
import json
import os

# 配置文件路径
CONFIG_DIR = 'd:/erp_thirteen/tp_education_system/backend/config'
TABLE_NAME_MAPPINGS_FILE = os.path.join(CONFIG_DIR, 'table_name_mappings.json')
MERGED_SCHEMA_FILE = os.path.join(CONFIG_DIR, 'merged_schema_mappings.json')
NAVIGATION_FILE = os.path.join(CONFIG_DIR, 'navigation.json')
FIELD_CONFIGS_DIR = os.path.join(CONFIG_DIR, 'field_configs')

print("=" * 80)
print("开始调查教师学历记录表的所有残留信息")
print("=" * 80)

# 1. 检查数据库
print("\n【1. 数据库检查】")
conn = psycopg2.connect(
    host='localhost',
    port=5432,
    database='taiping_education',
    user='taiping_user',
    password='taiping_password'
)
cursor = conn.cursor()

# 检查表是否存在
cursor.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public' 
    AND (table_name LIKE '%teacher%' OR table_name LIKE '%education%')
""")
tables = cursor.fetchall()
print(f"数据库中匹配的表: {[t[0] for t in tables]}")

# 检查表结构
cursor.execute("""
    SELECT table_name, column_name, data_type 
    FROM information_schema.columns 
    WHERE table_schema = 'public' 
    AND table_name = 'teacher_education_record'
    ORDER BY ordinal_position
""")
columns = cursor.fetchall()
if columns:
    print(f"\nteacher_education_record 表结构:")
    for col in columns:
        print(f"  - {col[1]}: {col[2]}")
else:
    print("\nteacher_education_record 表不存在")

cursor.close()
conn.close()

# 2. 检查 table_name_mappings.json
print("\n【2. table_name_mappings.json 检查】")
with open(TABLE_NAME_MAPPINGS_FILE, 'r', encoding='utf-8') as f:
    table_mappings = json.load(f)

mappings = table_mappings.get("mappings", {})
reverse_mappings = table_mappings.get("reverse_mappings", {})

# 查找所有与教师学历相关的映射
for cn_name, info in mappings.items():
    if '教师' in cn_name or '学历' in cn_name:
        print(f"  中文名: {cn_name}")
        print(f"  英文名: {info.get('english_name')}")
        print(f"  类型: {info.get('table_type')}")
        print(f"  字段签名: {info.get('field_signature', [])}")
        print()

# 3. 检查 merged_schema_mappings.json
print("\n【3. merged_schema_mappings.json 检查】")
with open(MERGED_SCHEMA_FILE, 'r', encoding='utf-8') as f:
    schema_config = json.load(f)

tables_config = schema_config.get("tables", {})
for table_name, config in tables_config.items():
    if 'teacher' in table_name or 'education' in table_name:
        print(f"\n  表名: {table_name}")
        print(f"  中文名: {config.get('chinese_name')}")
        print(f"  类型: {config.get('type')}")
        print(f"  字段数: {len(config.get('fields', []))}")
        if config.get('fields'):
            print(f"  字段列表:")
            for field in config.get('fields', []):
                source = field.get('sourceField', '')
                target = field.get('targetField', '')
                print(f"    - {source} -> {target}")

# 4. 检查 navigation.json
print("\n【4. navigation.json 检查】")
with open(NAVIGATION_FILE, 'r', encoding='utf-8') as f:
    navigation = json.load(f)

def find_in_navigation(modules, path=""):
    """递归查找导航中的教师学历记录"""
    found = []
    for module in modules:
        current_path = f"{path}/{module.get('title', '')}"
        title = module.get('title', '')
        table_name = module.get('table_name', '')
        
        if '教师学历' in title or 'teacher_education' in table_name:
            found.append({
                'path': current_path,
                'id': module.get('id'),
                'title': title,
                'table_name': table_name,
                'component': module.get('component')
            })
        
        if 'children' in module:
            found.extend(find_in_navigation(module['children'], current_path))
    
    return found

found_items = find_in_navigation(navigation.get('modules', []))
if found_items:
    print(f"\n  在导航中找到 {len(found_items)} 个相关节点:")
    for item in found_items:
        print(f"    - {item['path']}")
        print(f"      ID: {item['id']}")
        print(f"      表名: {item['table_name']}")
        print(f"      组件: {item['component']}")
else:
    print("\n  导航中没有找到相关节点")

# 5. 检查字段配置文件
print("\n【5. 字段配置文件检查】")
if os.path.exists(FIELD_CONFIGS_DIR):
    for filename in os.listdir(FIELD_CONFIGS_DIR):
        if 'teacher' in filename or 'education' in filename:
            filepath = os.path.join(FIELD_CONFIGS_DIR, filename)
            print(f"\n  找到配置文件: {filename}")
            with open(filepath, 'r', encoding='utf-8') as f:
                config = json.load(f)
            print(f"    表名: {config.get('table_name')}")
            print(f"    中文名: {config.get('chinese_name')}")
            print(f"    字段数: {len(config.get('fields', []))}")

print("\n" + "=" * 80)
print("调查完成")
print("=" * 80)
