#!/usr/bin/env python3
"""修复字段映射配置中的大括号格式"""
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
print("修复字段映射配置 - 将双大括号改为单大括号")
print("=" * 80)

# 获取模板ID 16 的所有字段映射
cursor.execute("""
    SELECT id, placeholder_name, intermediate_field
    FROM template_field_mapping
    WHERE template_id = 16
    ORDER BY id
""")

mappings = cursor.fetchall()
print(f"\n找到 {len(mappings)} 个字段映射")

fixed_count = 0
for m in mappings:
    mapping_id = m[0]
    placeholder = m[1]
    field = m[2]
    
    # 如果占位符是双大括号格式，改为单大括号
    if placeholder.startswith('{{') and placeholder.endswith('}}'):
        # 提取字段名
        field_name = placeholder[2:-2]
        new_placeholder = '{' + field_name + '}'
        
        # 更新数据库
        cursor.execute("""
            UPDATE template_field_mapping
            SET placeholder_name = %s
            WHERE id = %s
        """, (new_placeholder, mapping_id))
        
        fixed_count += 1
        print(f"  修复: {placeholder} -> {new_placeholder}")

conn.commit()
print(f"\n共修复 {fixed_count} 个字段映射")

# 验证结果
cursor.execute("""
    SELECT placeholder_name, intermediate_field
    FROM template_field_mapping
    WHERE template_id = 16
    ORDER BY placeholder_name
""")

print("\n" + "=" * 80)
print("修复后的字段映射")
print("=" * 80)
for m in cursor.fetchall():
    print(f"  {m[0]} -> {m[1]}")

cursor.close()
conn.close()

print("\n" + "=" * 80)
print("修复完成")
print("=" * 80)
