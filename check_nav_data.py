import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port='5432',
    database='taiping_education',
    user='taiping_user',
    password='taiping_password'
)
cursor = conn.cursor()

# 检查导航模块数据
cursor.execute("SELECT * FROM navigation_modules LIMIT 5")
rows = cursor.fetchall()

print(f'导航模块数量: {len(rows)}')
for row in rows:
    print(f'  {row}')

# 检查列名
cursor.execute("""
    SELECT column_name 
    FROM information_schema.columns 
    WHERE table_name = 'navigation_modules'
""")
columns = cursor.fetchall()
print(f'\n列名: {[col[0] for col in columns]}')

cursor.close()
conn.close()
