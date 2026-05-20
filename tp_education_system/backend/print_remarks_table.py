import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port='5432',
    database='taiping_education',
    user='taiping_user',
    password='taiping_password'
)

cursor = conn.cursor()

print('=' * 80)
print('performance_pay_remarks表结构：')
print('=' * 80)

# 获取表结构
cursor.execute("""
    SELECT column_name, data_type, character_maximum_length, is_nullable, column_default
    FROM information_schema.columns
    WHERE table_name='performance_pay_remarks'
    AND table_schema='public'
    ORDER BY ordinal_position
""")
fields = cursor.fetchall()

print('\n字段列表：')
print('-' * 80)
for field in fields:
    print(f'{field[0]:20s} | {field[1]:15s} | 长度={field[2]} | 可空={field[3]} | 默认值={field[4]}')

print('\n' + '=' * 80)
print('performance_pay_remarks表所有数据：')
print('=' * 80)

cursor.execute("""
    SELECT *
    FROM performance_pay_remarks
    ORDER BY id
""")
rows = cursor.fetchall()

print(f'\n总记录数: {len(rows)}')

for row in rows:
    print('\n' + '-' * 80)
    for i, field in enumerate(fields):
        print(f'{field[0]:20s} = {row[i]}')

cursor.close()
conn.close()
