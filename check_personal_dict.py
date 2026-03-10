import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port='5432',
    database='taiping_education',
    user='taiping_user',
    password='taiping_password'
)
cursor = conn.cursor()

# 检查 personal_dict_dictionary 表
print('1. personal_dict_dictionary 表结构：')
print('=' * 50)
cursor.execute("""
    SELECT column_name 
    FROM information_schema.columns 
    WHERE table_name = 'personal_dict_dictionary' AND table_schema = 'public'
    ORDER BY ordinal_position
""")
columns = [row[0] for row in cursor.fetchall()]
print(f"列名: {columns}")

# 检查数据
print('\n2. personal_dict_dictionary 表数据：')
print('=' * 50)
cursor.execute("SELECT * FROM personal_dict_dictionary LIMIT 10")
for row in cursor.fetchall():
    print(f"  {row}")

# 检查记录数
cursor.execute("SELECT COUNT(*) FROM personal_dict_dictionary")
count = cursor.fetchone()[0]
print(f'\n总记录数: {count}')

cursor.close()
conn.close()
