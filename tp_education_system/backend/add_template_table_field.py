"""
为 document_templates 表添加 intermediate_table 字段
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

# 检查字段是否已存在
cursor.execute("""
    SELECT column_name 
    FROM information_schema.columns 
    WHERE table_name = 'document_templates' AND column_name = 'intermediate_table'
""")

if not cursor.fetchone():
    # 添加 intermediate_table 字段
    cursor.execute("""
        ALTER TABLE document_templates 
        ADD COLUMN intermediate_table VARCHAR(100),
        ADD COLUMN intermediate_table_cn VARCHAR(100)
    """)
    conn.commit()
    print('已添加 intermediate_table 和 intermediate_table_cn 字段')
else:
    print('字段已存在')

# 为现有模板设置默认中间表
cursor.execute("""
    UPDATE document_templates 
    SET intermediate_table = 'retirement_report_data',
        intermediate_table_cn = '退休呈报数据'
    WHERE intermediate_table IS NULL
""")
conn.commit()
print('已为现有模板设置默认中间表')

cursor.close()
conn.close()
print('完成')
