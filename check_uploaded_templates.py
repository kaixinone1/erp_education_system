import psycopg2
import os

conn = psycopg2.connect(
    host='localhost',
    port='5432',
    database='taiping_education',
    user='taiping_user',
    password='taiping_password'
)
cursor = conn.cursor()

# 查看已上传的模板
cursor.execute("""
    SELECT template_id, template_name, file_path, file_type, placeholders
    FROM universal_templates
    ORDER BY created_at DESC
""")

print('已上传的模板：')
for row in cursor.fetchall():
    print(f'  模板ID: {row[0]}')
    print(f'  模板名: {row[1]}')
    print(f'  文件路径: {row[2]}')
    print(f'  文件类型: {row[3]}')
    print(f'  占位符: {row[4]}')
    print(f'  文件存在: {os.path.exists(row[2]) if row[2] else False}')
    print()

cursor.close()
conn.close()
