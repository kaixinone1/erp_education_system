import psycopg2

conn = psycopg2.connect(host='localhost', port='5432', database='taiping_education', user='taiping_user', password='taiping_password')
cursor = conn.cursor()

# 检查所有包含"职务升降"的模板
cursor.execute("""
    SELECT template_id, template_name, file_path 
    FROM document_templates 
    WHERE template_id LIKE '%职务升降%'
""")

rows = cursor.fetchall()

print('找到的相关模板:')
for row in rows:
    print(f'  ID: {row[0]}')
    print(f'  名称: {row[1]}')
    print(f'  路径: {row[2]}')
    print()

if not rows:
    print('没有找到相关模板')

cursor.close()
conn.close()
