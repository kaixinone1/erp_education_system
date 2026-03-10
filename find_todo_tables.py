import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port='5432',
    database='taiping_education',
    user='taiping_user',
    password='taiping_password'
)
cursor = conn.cursor()

# 查找所有可能的待办工作相关表
cursor.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public' 
    AND (
        table_name LIKE '%todo%' 
        OR table_name LIKE '%work%'
        OR table_name LIKE '%task%'
        OR table_name LIKE '%待办%'
        OR table_name LIKE '%清单%'
    )
    ORDER BY table_name
""")

tables = cursor.fetchall()

print('找到的相关表:')
for t in tables:
    table_name = t[0]
    print(f'\n=== {table_name} ===')
    
    # 获取列信息
    cursor.execute(f"""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = '{table_name}'
        ORDER BY ordinal_position
    """)
    columns = cursor.fetchall()
    print('列:')
    for col in columns:
        print(f'  {col[0]}: {col[1]}')
    
    # 获取数据条数
    try:
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f'数据条数: {count}')
        
        # 如果有数据，显示前3条
        if count > 0:
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
            rows = cursor.fetchall()
            print('前3条数据:')
            for i, row in enumerate(rows):
                print(f'  行{i+1}: {row}')
    except Exception as e:
        print(f'查询失败: {e}')

cursor.close()
conn.close()
