import psycopg2
conn = psycopg2.connect(host='localhost', port='5432', database='taiping_education', user='taiping_user', password='taiping_password')
cursor = conn.cursor()

# 查看教师基础信息表的字段
cursor.execute("""
    SELECT column_name, data_type
    FROM information_schema.columns
    WHERE table_name = 'teacher_basic_info'
    ORDER BY ordinal_position
""")
print('teacher_basic_info 表字段:')
for row in cursor.fetchall():
    print(f'  {row[0]} - {row[1]}')

# 查看一条示例数据
cursor.execute('SELECT * FROM teacher_basic_info LIMIT 1')
row = cursor.fetchone()
if row:
    print('\n示例数据:')
    cursor.execute("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'teacher_basic_info'
        ORDER BY ordinal_position
    """)
    cols = [r[0] for r in cursor.fetchall()]
    for i, col in enumerate(cols[:10]):
        print(f'  {col}: {row[i]}')

cursor.close()
conn.close()
