import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port='5432',
    database='taiping_education',
    user='taiping_user',
    password='taiping_password'
)
cursor = conn.cursor()

# 查找包含field_76的表
cursor.execute("""
    SELECT table_name, column_name
    FROM information_schema.columns
    WHERE column_name LIKE '%field_76%' AND table_schema = 'public'
""")
rows = cursor.fetchall()
print('包含 field_76 的表:')
for row in rows:
    print(f'  表: {row[0]}, 字段: {row[1]}')

# 查找包含unnamed的表
cursor.execute("""
    SELECT table_name, column_name
    FROM information_schema.columns
    WHERE column_name LIKE '%unnamed%' AND table_schema = 'public'
""")
rows = cursor.fetchall()
print('\n包含 unnamed 的表:')
for row in rows:
    print(f'  表: {row[0]}, 字段: {row[1]}')

cursor.close()
conn.close()
