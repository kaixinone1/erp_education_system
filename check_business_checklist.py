import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port='5432',
    database='taiping_education',
    user='taiping_user',
    password='taiping_password'
)
cursor = conn.cursor()

# 检查 business_checklist 表
cursor.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = 'business_checklist'
    ORDER BY ordinal_position
""")

columns = cursor.fetchall()
print('business_checklist 表字段:')
for col in columns:
    print(f'  {col[0]}: {col[1]}')

# 获取数据条数
cursor.execute("SELECT COUNT(*) FROM business_checklist")
count = cursor.fetchone()[0]
print(f'\n数据条数: {count}')

# 显示前3条数据
if count > 0:
    cursor.execute("SELECT * FROM business_checklist LIMIT 3")
    rows = cursor.fetchall()
    print('\n前3条数据:')
    for i, row in enumerate(rows):
        print(f'\n行{i+1}:')
        for j, col in enumerate(columns):
            if j < len(row):
                print(f'  {col[0]}: {row[j]}')

cursor.close()
conn.close()
