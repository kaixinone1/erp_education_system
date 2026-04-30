#!/usr/bin/env python3
"""找出哪些有数据的占位符没有被替换"""
import re
import psycopg2

DATABASE_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "database": "taiping_education",
    "user": "taiping_user",
    "password": "taiping_password"
}

# 读取模板
template_path = 'templates/职工退休申报表html.html'
with open(template_path, 'r', encoding='utf-8') as f:
    content = f.read()

print("=" * 80)
print("找出有数据但未被替换的占位符")
print("=" * 80)

# 提取所有占位符
placeholders = set()

# 1. 被HTML标签分割的双大括号
split_pattern = r'<[^>]*>\{</[^>]*>\{([^{}]+)\}<[^>]*>\}</[^>]*>'
for match in re.findall(split_pattern, content):
    field_name = match.strip()
    if field_name and len(field_name) < 50:
        placeholders.add(field_name)

# 2. 双大括号
double_pattern = r'\{\{([^{}]+)\}\}'
for match in re.findall(double_pattern, content):
    field_name = match.strip()
    if field_name and len(field_name) < 50:
        placeholders.add(field_name)

# 3. 单大括号
single_pattern = r'\{([^{}]+)\}'
for match in re.findall(single_pattern, content):
    field_name = match.strip()
    if any(c in field_name for c in [';', '\n', '\t', 'mso-', 'font:', 'border:', 'color:', 'style:', 'background', 'padding', 'margin']):
        continue
    if '<' in field_name or '>' in field_name:
        continue
    if field_name and len(field_name) < 50:
        if re.search(r'[\u4e00-\u9fa5a-zA-Z]', field_name):
            placeholders.add(field_name)

print(f"\n模板中提取到 {len(placeholders)} 个占位符")

# 获取字段映射
conn = psycopg2.connect(**DATABASE_CONFIG)
cursor = conn.cursor()
cursor.execute("""
    SELECT placeholder_name, intermediate_table, intermediate_field
    FROM template_field_mapping
    WHERE template_id = 16 AND is_active = true
""")

mapping_dict = {}
for row in cursor.fetchall():
    placeholder = row[0].strip()
    if placeholder.startswith('{{') and placeholder.endswith('}}'):
        placeholder = placeholder[2:-2]
    elif placeholder.startswith('{') and placeholder.endswith('}'):
        placeholder = placeholder[1:-1]
    mapping_dict[placeholder] = (row[1], row[2])

cursor.close()
conn.close()

print(f"数据库中有 {len(mapping_dict)} 个字段映射")

# 检查每个配置的占位符是否有数据
print("\n" + "=" * 80)
print("检查已配置的占位符：")
print("=" * 80)

for ph in sorted(placeholders):
    if ph in mapping_dict:
        table, field = mapping_dict[ph]
        
        # 查询数据
        conn = psycopg2.connect(**DATABASE_CONFIG)
        cursor = conn.cursor()
        cursor.execute(f"SELECT {field} FROM {table} WHERE teacher_id = %s", (273,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        
        value = str(row[0]) if row and row[0] else ''
        
        if value:
            print(f"  ✓ {ph}: 有数据 [{value[:30]}]")
        else:
            print(f"  ✗ {ph}: 无数据 (已配置但中间表为空)")
    else:
        print(f"  ✗ {ph}: 未配置映射")

print("\n" + "=" * 80)
