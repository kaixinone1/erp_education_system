import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port='5432',
    database='taiping_education',
    user='taiping_user',
    password='taiping_password'
)
cursor = conn.cursor()

# 获取 id_card 表中的所有身份证
cursor.execute("SELECT DISTINCT id_card FROM id_card WHERE id_card IS NOT NULL")
id_card_ids = set(row[0] for row in cursor.fetchall())
print(f'id_card 表中的身份证数量: {len(id_card_ids)}')

# 获取 teacher_basic_info 表中的所有身份证
cursor.execute("SELECT DISTINCT id_card FROM teacher_basic_info WHERE id_card IS NOT NULL")
teacher_ids = set(row[0] for row in cursor.fetchall())
print(f'teacher_basic_info 表中的身份证数量: {len(teacher_ids)}')

# 计算匹配率
matched = id_card_ids & teacher_ids
only_in_id_card = id_card_ids - teacher_ids

print(f'\n匹配情况:')
print(f'  匹配的身份证: {len(matched)} 个')
print(f'  只在 id_card 表中: {len(only_in_id_card)} 个')

if only_in_id_card:
    print(f'\n前10个未匹配的身份证:')
    for id_card in list(only_in_id_card)[:10]:
        print(f'  {id_card}')

cursor.close()
conn.close()
