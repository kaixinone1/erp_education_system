import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port='5432',
    database='taiping_education',
    user='taiping_user',
    password='taiping_password'
)
cursor = conn.cursor()

# 查看字段映射表结构
cursor.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = 'template_field_mapping'
    ORDER BY ordinal_position
""")

print('template_field_mapping 表结构:')
for row in cursor.fetchall():
    print(f'  {row[0]}: {row[1]}')

# 查看现有数据示例
cursor.execute('SELECT * FROM template_field_mapping LIMIT 2')
rows = cursor.fetchall()
if rows:
    print('\n示例数据:')
    cursor.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'template_field_mapping'
        ORDER BY ordinal_position
    """)
    cols = [r[0] for r in cursor.fetchall()]
    for row in rows:
        for i, col in enumerate(cols):
            print(f'  {col}: {row[i]}')
        print()

cursor.close()
conn.close()
