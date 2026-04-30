import psycopg2
conn = psycopg2.connect(host='localhost', port='5432', database='taiping_education', user='taiping_user', password='taiping_password')
cur = conn.cursor()

# 查看todo_history表结构
cur.execute('''
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = 'todo_history'
    ORDER BY ordinal_position
''')
print('=== todo_history 表结构 ===')
for row in cur.fetchall():
    print(f'  {row[0]}: {row[1]}')

conn.close()
