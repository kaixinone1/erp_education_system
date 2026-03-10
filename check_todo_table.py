import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port='5432',
    database='taiping_education',
    user='taiping_user',
    password='taiping_password'
)
cursor = conn.cursor()

# 检查表是否存在
cursor.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public' AND table_name LIKE '%todo%'
""")

tables = cursor.fetchall()
print('找到的todo相关表:')
for t in tables:
    print(f'  - {t[0]}')
    # 检查列
    cursor.execute(f"""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = '{t[0]}'
    """)
    columns = cursor.fetchall()
    for col in columns:
        print(f'      {col[0]}: {col[1]}')
    print()

cursor.close()
conn.close()
