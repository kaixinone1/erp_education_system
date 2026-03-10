import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port='5432',
    database='taiping_education',
    user='taiping_user',
    password='taiping_password'
)
cursor = conn.cursor()

# 查看 document_templates 表结构
cursor.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = 'document_templates' AND table_schema = 'public'
    ORDER BY ordinal_position
""")

print('document_templates 表结构：')
for row in cursor.fetchall():
    print(f'  {row[0]}: {row[1]}')

# 查看不同模板的 intermediate_table 配置
cursor.execute("""
    SELECT template_id, file_path, intermediate_table
    FROM document_templates 
    ORDER BY template_id
""")

print('\n模板的中间表配置：')
for row in cursor.fetchall():
    print(f'  {row[0]}: {row[2]}')

cursor.close()
conn.close()
