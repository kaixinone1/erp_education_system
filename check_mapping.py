import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port='5432',
    database='taiping_education',
    user='taiping_user',
    password='taiping_password'
)
cursor = conn.cursor()

# 查找不同模板使用的中间表
cursor.execute("""
    SELECT DISTINCT template_id, intermediate_table 
    FROM template_field_mapping 
    ORDER BY template_id
""")

print('模板与中间表映射：')
current_template = None
for row in cursor.fetchall():
    if row[0] != current_template:
        print(f'\n模板: {row[0]}')
        current_template = row[0]
    print(f'  中间表: {row[1]}')

cursor.close()
conn.close()
