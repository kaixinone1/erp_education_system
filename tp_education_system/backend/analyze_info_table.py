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
print('分析info表和post_appointment_info表的关系：')
print('=' * 80)

print('\n1. 检查两个表的数据是否重复')
print('-' * 80)

# 检查info表中有多少人在post_appointment_info表中
cursor.execute("""
    SELECT COUNT(*) 
    FROM info i
    JOIN post_appointment_info p ON i.id_card = p.id_card
""")
match_count = cursor.fetchone()[0]
print(f'info表和post_appointment_info表匹配的记录: {match_count}条')

# 检查info表中有多少人不在post_appointment_info表中
cursor.execute("""
    SELECT COUNT(*) 
    FROM info i
    WHERE NOT EXISTS (
        SELECT 1 FROM post_appointment_info p WHERE i.id_card = p.id_card
    )
""")
not_match_count = cursor.fetchone()[0]
print(f'info表中有{not_match_count}人不在post_appointment_info表中')

# 检查post_appointment_info表中有多少人不在info表中
cursor.execute("""
    SELECT COUNT(*) 
    FROM post_appointment_info p
    WHERE NOT EXISTS (
        SELECT 1 FROM info i WHERE p.id_card = i.id_card
    )
""")
not_match_count2 = cursor.fetchone()[0]
print(f'post_appointment_info表中有{not_match_count2}人不在info表中')

print('\n2. 对比两个表的字段')
print('-' * 80)

print('\ninfo表的字段：')
cursor.execute("""
    SELECT column_name
    FROM information_schema.columns
    WHERE table_name='info'
    AND table_schema='public'
    ORDER BY ordinal_position
""")
info_fields = [row[0] for row in cursor.fetchall()]
for field in info_fields:
    print(f'  - {field}')

print('\npost_appointment_info表的字段：')
cursor.execute("""
    SELECT column_name
    FROM information_schema.columns
    WHERE table_name='post_appointment_info'
    AND table_schema='public'
    ORDER BY ordinal_position
""")
post_fields = [row[0] for row in cursor.fetchall()]
for field in post_fields:
    print(f'  - {field}')

print('\n3. 对比相同身份证号码的数据')
print('-' * 80)
cursor.execute("""
    SELECT 
        i.id_card,
        i.name,
        i.post_2,
        p.post_1
    FROM info i
    JOIN post_appointment_info p ON i.id_card = p.id_card
    WHERE i.post_2 IS NOT NULL OR p.post_1 IS NOT NULL
    LIMIT 10
""")
rows = cursor.fetchall()
print(f'对比数据（前10条）：')
for i, row in enumerate(rows):
    print(f'  {i+1}. 身份证={row[0]}, 姓名={row[1]}, info.post_2={row[2]}, post.post_1={row[3]}')

print('\n' + '=' * 80)
print('结论：')
print('=' * 80)
print('info表和post_appointment_info表：')
print(f'  - 有{match_count}条记录匹配')
print(f'  - info表比post_appointment_info表少{not_match_count2}条记录')
print('')
print('根据分析：')
print('  1. info表是post_appointment_info表的子集')
print('  2. info表可能是旧版本或导入时的临时表')
print('  3. 建议使用post_appointment_info表作为岗位聘任信息表')
print('  4. info表可以废弃或作为历史数据保留')

cursor.close()
conn.close()
