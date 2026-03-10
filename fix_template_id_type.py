import psycopg2

conn = psycopg2.connect(host='localhost', port='5432', database='taiping_education', user='taiping_user', password='taiping_password')
cursor = conn.cursor()

# 修改 template_field_mapping 表的 template_id 字段类型
try:
    cursor.execute("""
        ALTER TABLE template_field_mapping 
        ALTER COLUMN template_id TYPE VARCHAR(255)
    """)
    conn.commit()
    print('成功修改 template_field_mapping 表的 template_id 字段为 VARCHAR(255)')
except Exception as e:
    print(f'修改失败: {e}')
    conn.rollback()

# 检查是否还有其他表需要修改
tables_to_check = [
    'template_page_settings',
    'template_placeholders',
    'template_field_mappings'
]

for table in tables_to_check:
    try:
        cursor.execute(f"""
            SELECT data_type 
            FROM information_schema.columns 
            WHERE table_name = '{table}' AND column_name = 'template_id'
        """)
        row = cursor.fetchone()
        if row:
            print(f'{table}.template_id 类型: {row[0]}')
    except Exception as e:
        print(f'检查 {table} 失败: {e}')

cursor.close()
conn.close()
