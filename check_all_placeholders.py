import psycopg2

conn = psycopg2.connect(host='localhost', port='5432', database='taiping_education', user='taiping_user', password='taiping_password')
cursor = conn.cursor()

# 查询所有模板的占位符
cursor.execute("""
    SELECT template_id, placeholder_name, created_at 
    FROM template_placeholders 
    WHERE template_id LIKE '%枣阳市机关事业单位%'
    ORDER BY template_id, created_at DESC
""")

rows = cursor.fetchall()

print('相关模板的占位符:')
current_template = None
for row in rows:
    template_id, placeholder_name, created_at = row
    if template_id != current_template:
        current_template = template_id
        print(f'\n模板: {template_id}')
    print(f'  - {placeholder_name} ({created_at})')

if not rows:
    print('没有找到相关占位符')

cursor.close()
conn.close()
