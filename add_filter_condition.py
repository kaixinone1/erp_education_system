import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port='5432',
    database='taiping_education',
    user='taiping_user',
    password='taiping_password'
)
cursor = conn.cursor()

# 检查 filter_condition 字段是否存在
cursor.execute("""
    SELECT column_name 
    FROM information_schema.columns 
    WHERE table_name = 'template_field_mapping' AND column_name = 'filter_condition'
""")

if not cursor.fetchone():
    # 添加字段
    cursor.execute("""
        ALTER TABLE template_field_mapping 
        ADD COLUMN filter_condition VARCHAR(500) DEFAULT ''
    """)
    print('添加 filter_condition 字段成功')
else:
    print('filter_condition 字段已存在')

conn.commit()
cursor.close()
conn.close()
