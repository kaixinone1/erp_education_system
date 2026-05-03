import psycopg2
conn = psycopg2.connect(host='localhost', port='5432', database='taiping_education', user='taiping_user', password='taiping_password')
cursor = conn.cursor()

# 删除重复数据，保留每组最新的一条
cursor.execute('''
    DELETE FROM salary_data
    WHERE id IN (
        SELECT id FROM (
            SELECT id, ROW_NUMBER() OVER (PARTITION BY id_card_1, name, unit ORDER BY created_at DESC) as rn
            FROM salary_data
        ) t
        WHERE t.rn > 1
    )
''')
deleted = cursor.rowcount
conn.commit()

# 检查清理后的数据量
cursor.execute('SELECT COUNT(*) FROM salary_data')
count = cursor.fetchone()[0]

# 检查唯一人数
cursor.execute('SELECT COUNT(DISTINCT id_card_1) FROM salary_data')
unique_count = cursor.fetchone()[0]

print(f'删除重复数据: {deleted}条')
print(f'清理后数据量: {count}条')
print(f'唯一人数: {unique_count}人')

cursor.close()
conn.close()