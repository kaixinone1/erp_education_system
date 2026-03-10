import psycopg2

conn = psycopg2.connect(host='localhost', port='5432', database='taiping_education', user='taiping_user', password='taiping_password')
cursor = conn.cursor()

# 查询所有相关模板的字段映射
cursor.execute("""
    SELECT template_id, field_name, field_label, created_at 
    FROM template_field_mappings 
    WHERE template_id LIKE '%枣阳市机关事业单位%'
    ORDER BY template_id, created_at DESC
""")

rows = cursor.fetchall()

print('相关模板的字段映射:')
current_template = None
for row in rows:
    template_id, field_name, field_label, created_at = row
    if template_id != current_template:
        current_template = template_id
        print(f'\n模板: {template_id}')
    print(f'  - {field_name} ({field_label}) - {created_at}')

if not rows:
    print('没有找到相关字段映射')

cursor.close()
conn.close()
