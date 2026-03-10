import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port='5432',
    database='taiping_education',
    user='taiping_user',
    password='taiping_password'
)
cursor = conn.cursor()

# 检查 personal_dict_dictionary 表的字段
cursor.execute("""
    SELECT column_name 
    FROM information_schema.columns 
    WHERE table_name = 'personal_dict_dictionary' AND table_schema = 'public'
    ORDER BY ordinal_position
""")
print('personal_dict_dictionary 表字段:')
for row in cursor.fetchall():
    print(f'  {row[0]}')

# 尝试用 biao_qian 字段查询
cursor.execute('SELECT id, biao_qian FROM personal_dict_dictionary LIMIT 5')
print('\n使用 biao_qian 字段查询:')
for row in cursor.fetchall():
    print(f'  id={row[0]}, biao_qian={row[1]}')

# 尝试用 标签 字段查询
try:
    cursor.execute('SELECT id, "标签" FROM personal_dict_dictionary LIMIT 5')
    print('\n使用 "标签" 字段查询:')
    for row in cursor.fetchall():
        print(f'  id={row[0]}, 标签={row[1]}')
except Exception as e:
    print(f'\n使用 "标签" 字段查询失败: {e}')

# 检查是否有基础工资这个标签
cursor.execute("SELECT * FROM personal_dict_dictionary WHERE biao_qian = '基础工资'")
result = cursor.fetchall()
print(f'\n查询 "基础工资": {result}')

cursor.close()
conn.close()
