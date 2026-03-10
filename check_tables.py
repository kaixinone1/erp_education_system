import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port='5432',
    database='taiping_education',
    user='taiping_user',
    password='taiping_password'
)
cursor = conn.cursor()

# 获取所有表
cursor.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
    ORDER BY table_name
""")

print('数据库中的所有表：')
print('=' * 50)
for row in cursor.fetchall():
    print(f'  {row[0]}')

# 查找包含身份证或属性的表
cursor.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public' 
    AND table_type = 'BASE TABLE'
    AND (table_name LIKE '%identity%' 
         OR table_name LIKE '%card%'
         OR table_name LIKE '%属性%'
         OR table_name LIKE '%身份证%')
    ORDER BY table_name
""")

print('\n可能的身份证属性相关表：')
print('=' * 50)
rows = cursor.fetchall()
if rows:
    for row in rows:
        print(f'  {row[0]}')
else:
    print('  未找到相关表')

cursor.close()
conn.close()
