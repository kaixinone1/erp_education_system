"""
检查模板 16 和 21 的详细信息
"""
import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port='5432',
    database='taiping_education',
    user='taiping_user',
    password='taiping_password'
)
cursor = conn.cursor()

# 检查模板 16 和 21 的信息
cursor.execute("""
    SELECT template_id, template_name, file_path, intermediate_table, intermediate_table_cn
    FROM document_templates
    WHERE template_id IN ('16', '21')
""")

print('模板 16 和 21 的信息:')
for row in cursor.fetchall():
    print(f'  模板ID: {row[0]}')
    print(f'  模板名称: {row[1]}')
    print(f'  文件路径: {row[2]}')
    print(f'  中间表: {row[3]}')
    print(f'  中间表中文: {row[4]}')
    print('---')

# 检查模板 16 的字段映射
cursor.execute("""
    SELECT placeholder_name, intermediate_table, intermediate_field
    FROM template_field_mapping
    WHERE template_id = '16' AND is_active = true
    LIMIT 10
""")

print('\n模板 16 的字段映射（前10条）:')
for row in cursor.fetchall():
    print(f'  占位符: {row[0]} -> {row[1]}.{row[2]}')

# 检查模板 21 的字段映射
cursor.execute("""
    SELECT placeholder_name, intermediate_table, intermediate_field
    FROM template_field_mapping
    WHERE template_id = '21' AND is_active = true
    LIMIT 10
""")

print('\n模板 21 的字段映射（前10条）:')
for row in cursor.fetchall():
    print(f'  占位符: {row[0]} -> {row[1]}.{row[2]}')

cursor.close()
conn.close()
