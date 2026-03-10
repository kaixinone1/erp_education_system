import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port='5432',
    database='taiping_education',
    user='taiping_user',
    password='taiping_password'
)
cursor = conn.cursor()

# 查找包含 todo 的表
cursor.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public' 
    AND table_type = 'BASE TABLE'
    AND table_name LIKE '%todo%'
    ORDER BY table_name
""")

print('包含 todo 的表：')
for row in cursor.fetchall():
    print(f'  {row[0]}')

cursor.close()
conn.close()
