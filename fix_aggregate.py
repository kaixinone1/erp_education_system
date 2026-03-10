import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port='5432',
    database='taiping_education',
    user='taiping_user',
    password='taiping_password'
)
cursor = conn.cursor()

# 检查 aggregate_func 字段是否存在
cursor.execute("""
    SELECT column_name 
    FROM information_schema.columns 
    WHERE table_name = 'template_field_mapping' AND column_name = 'aggregate_func'
""")

if not cursor.fetchone():
    # 添加字段
    cursor.execute("""
        ALTER TABLE template_field_mapping 
        ADD COLUMN aggregate_func VARCHAR(20) DEFAULT ''
    """)
    print('添加 aggregate_func 字段成功')
else:
    print('aggregate_func 字段已存在')

conn.commit()
cursor.close()
conn.close()
