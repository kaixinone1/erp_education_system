"""
列出所有存在的模板
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
    SELECT template_id, template_name, file_path, intermediate_table
    FROM document_templates
    ORDER BY template_id
""")

print('所有存在的模板:')
print('-' * 80)
for row in cursor.fetchall():
    print(f'ID: {row[0]}')
    print(f'名称: {row[1]}')
    print(f'文件: {row[2]}')
    print(f'中间表: {row[3]}')
    print('-' * 80)

cursor.close()
conn.close()
