"""
检查字段映射配置中的占位符格式
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

# 检查职工退休呈报表html的字段映射配置
cursor.execute("""
    SELECT placeholder_name, intermediate_field
    FROM template_field_mapping
    WHERE template_id = '职工退休呈报表html' AND is_active = true
    LIMIT 10
""")

print('职工退休呈报表html 的字段映射配置（前10条）:')
for row in cursor.fetchall():
    placeholder_name = row[0]
    intermediate_field = row[1]
    print(f'  占位符: "{placeholder_name}" -> 字段: "{intermediate_field}"')

cursor.close()
conn.close()
