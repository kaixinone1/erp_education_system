import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port='5432',
    database='taiping_education',
    user='taiping_user',
    password='taiping_password'
)
cursor = conn.cursor()

# 查看所有业务清单表
cursor.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public' 
    AND (table_name LIKE '%_form' OR table_name LIKE '%report' OR table_name LIKE '%data')
    ORDER BY table_name
""")

print('业务数据表：')
for row in cursor.fetchall():
    print(f'  {row[0]}')

cursor.close()
conn.close()
