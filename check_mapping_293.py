"""
检查模板字段映射配置
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

template_id = '枣阳市机关事业单位养老保险改革过渡期内职务升降退休人员信息申报表htm'

# 检查模板信息
cursor.execute("""
    SELECT template_id, file_path, intermediate_table
    FROM document_templates
    WHERE template_id = %s
""", (template_id,))

template_row = cursor.fetchone()
if template_row:
    print(f'模板信息:')
    print(f'  template_id: {template_row[0]}')
    print(f'  file_path: {template_row[1]}')
    print(f'  intermediate_table: {template_row[2]}')
else:
    print('模板不存在！')

# 检查字段映射配置
cursor.execute("""
    SELECT placeholder_name, intermediate_table, intermediate_field
    FROM template_field_mapping
    WHERE template_id = %s AND is_active = true
    LIMIT 10
""", (template_id,))

rows = cursor.fetchall()
print(f'\n字段映射配置（前10条）:')
for row in rows:
    print(f'  占位符: "{row[0]}" -> 表: "{row[1]}" -> 字段: "{row[2]}"')

cursor.close()
conn.close()
