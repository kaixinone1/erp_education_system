import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port='5432',
    database='taiping_education',
    user='taiping_user',
    password='taiping_password'
)
cursor = conn.cursor()

# 查找包含"退休"的模板
cursor.execute("""
    SELECT template_id, file_path, file_name 
    FROM document_templates 
    WHERE file_name LIKE '%退休%' OR template_id LIKE '%退休%'
    ORDER BY template_id
""")

print('包含"退休"的模板：')
for row in cursor.fetchall():
    print(f'  template_id: {row[0]}')
    print(f'  file_path: {row[1]}')
    print(f'  file_name: {row[2]}')
    print()

cursor.close()
conn.close()
