import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port='5432',
    database='taiping_education',
    user='taiping_user',
    password='taiping_password'
)
cursor = conn.cursor()

# 检查 template_field_mapping 表结构
cursor.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = 'template_field_mapping'
    ORDER BY ordinal_position
""")

print('template_field_mapping 表结构:')
for row in cursor.fetchall():
    print(f'  {row[0]}: {row[1]}')

# 查看几条示例数据
cursor.execute("""
    SELECT * FROM template_field_mapping
    WHERE template_id = '16'
    LIMIT 5
""")

print('\n模板 16 的字段映射示例:')
columns = [desc[0] for desc in cursor.description]
rows = cursor.fetchall()
for row in rows:
    for i, col in enumerate(columns):
        print(f'  {col}: {row[i]}')
    print('---')

cursor.close()
conn.close()
