"""
直接测试查询
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

# 测试查询
cursor.execute("""
    SELECT 姓名 FROM retirement_report_data WHERE teacher_id = 293
""")

row = cursor.fetchone()
print(f'查询结果: {row}')

# 测试占位符处理
placeholder = '{{姓名}}'
field_name = placeholder.strip('{}')
print(f'占位符: {placeholder}')
print(f'处理后: {field_name}')

cursor.close()
conn.close()
