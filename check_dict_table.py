import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port='5432',
    database='taiping_education',
    user='taiping_user',
    password='taiping_password'
)
cursor = conn.cursor()

# 查看字典表数据
cursor.execute("SELECT * FROM dict_dictionary ORDER BY id DESC LIMIT 10")
rows = cursor.fetchall()

print('字典表 dict_dictionary 中的数据:')
print(f'总共有 {len(rows)} 条记录(显示最新10条)')

if rows:
    # 获取列名
    cursor.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'dict_dictionary'
        ORDER BY ordinal_position
    """)
    cols = [r[0] for r in cursor.fetchall()]
    print(f'\n列名: {cols}')
    print('\n数据:')
    for row in rows:
        print(f'  {row}')

cursor.close()
conn.close()
