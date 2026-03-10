import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port='5432',
    database='taiping_education',
    user='taiping_user',
    password='taiping_password'
)
cursor = conn.cursor()

# 检查每个模板关联的中间表
cursor.execute("""
    SELECT DISTINCT template_id, intermediate_table, intermediate_table_cn
    FROM template_field_mapping
    WHERE intermediate_table IS NOT NULL AND intermediate_table != ''
    ORDER BY template_id
""")

print('模板关联的中间表:')
for row in cursor.fetchall():
    print(f'  模板: {row[0]}, 中间表: {row[1]} ({row[2]})')

# 检查 document_templates 表是否有中间表字段
cursor.execute("""
    SELECT column_name 
    FROM information_schema.columns 
    WHERE table_name = 'document_templates'
""")

columns = [row[0] for row in cursor.fetchall()]
print(f'\ndocument_templates 表字段: {columns}')

cursor.close()
conn.close()
