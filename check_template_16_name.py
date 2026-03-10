"""
查询模板16的名称
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

cursor.execute("""
    SELECT template_id, template_name, file_path 
    FROM document_templates 
    WHERE template_id = '16'
""")

row = cursor.fetchone()
if row:
    print(f'模板ID: {row[0]}')
    print(f'模板名称: {row[1]}')
    print(f'文件路径: {row[2]}')
else:
    print('模板16不存在')

cursor.close()
conn.close()
