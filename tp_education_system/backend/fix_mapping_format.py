#!/usr/bin/env python3
import psycopg2

DATABASE_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "database": "taiping_education",
    "user": "taiping_user",
    "password": "taiping_password"
}

conn = psycopg2.connect(**DATABASE_CONFIG)
cursor = conn.cursor()

print("=" * 80)
print("修复字段映射格式 - 同时添加单大括号和双大括号映射")
print("=" * 80)

# 获取模板ID 16 的所有字段映射
cursor.execute("""
    SELECT id, placeholder_name, intermediate_table, intermediate_field
    FROM template_field_mapping
    WHERE template_id = 16
    ORDER BY id
""")

mappings = cursor.fetchall()
print(f"\n模板ID 16 现有 {len(mappings)} 个映射")

# 为每个映射同时添加单大括号版本
added_count = 0
for m in mappings:
    mapping_id = m[0]
    placeholder = m[1]
    table = m[2]
    field = m[3]
    
    # 如果占位符是双大括号格式，同时添加单大括号版本
    if placeholder.startswith('{{') and placeholder.endswith('}}'):
        # 提取字段名（去掉双大括号）
        field_name = placeholder[2:-2]
        single_brace = '{' + field_name + '}'
        
        # 检查是否已存在单大括号版本
        cursor.execute("""
            SELECT COUNT(*) FROM template_field_mapping
            WHERE template_id = 16 AND placeholder_name = %s
        """, (single_brace,))
        
        if cursor.fetchone()[0] == 0:
            # 添加单大括号版本
            cursor.execute("""
                INSERT INTO template_field_mapping 
                (template_id, template_name, placeholder_name, 
                 intermediate_table, intermediate_table_cn,
                 intermediate_field, intermediate_field_cn, is_active)
                VALUES (16, '职工退休申报表.html', %s, %s, '退休呈报数据', %s, %s, true)
            """, (single_brace, table, field, field))
            added_count += 1
            print(f"  添加单大括号映射: {single_brace} -> {table}.{field}")

conn.commit()
print(f"\n共添加 {added_count} 个单大括号映射")

# 验证结果
cursor.execute("""
    SELECT placeholder_name, intermediate_field
    FROM template_field_mapping
    WHERE template_id = 16
    ORDER BY placeholder_name
""")

all_mappings = cursor.fetchall()
print(f"\n修复后模板ID 16 共有 {len(all_mappings)} 个映射")

cursor.close()
conn.close()

print("\n" + "=" * 80)
print("修复完成")
print("=" * 80)
