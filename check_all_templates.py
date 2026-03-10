import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port='5432',
    database='taiping_education',
    user='taiping_user',
    password='taiping_password'
)
cursor = conn.cursor()

# 查看所有模板
cursor.execute("""
    SELECT template_id, file_path 
    FROM document_templates 
    WHERE file_path LIKE '%docx%' OR file_path LIKE '%htm%'
    ORDER BY template_id
""")

print('所有模板：')
for row in cursor.fetchall():
    print(f'  {row[0]}')
    print(f'    {row[1]}')

cursor.close()
conn.close()
