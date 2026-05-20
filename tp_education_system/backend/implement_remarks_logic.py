import psycopg2
from datetime import datetime

conn = psycopg2.connect(
    host='localhost',
    port='5432',
    database='taiping_education',
    user='taiping_user',
    password='taiping_password'
)

cursor = conn.cursor()

print('=' * 80)
print('实现备注信息统计逻辑：')
print('=' * 80)

year = 2026
month = 5
report_month = f"{year}-{month:02d}"

print(f'\n统计期间: {report_month}')

print('\n1. 教师基础信息表：任职状态变化')
print('-' * 80)
print('查询条件：updated_at在指定月份')
cursor.execute("""
    SELECT 
        t.id,
        t.id_card,
        t.name,
        t.employment_status,
        t.updated_at
    FROM teacher_basic_info t
    WHERE t.updated_at >= %s AND t.updated_at < %s
    ORDER BY t.updated_at DESC
""", (f'{report_month}-01', f'{year}-{month+1:02d}-01' if month < 12 else f'{year+1}-01-01'))
status_changes = cursor.fetchall()
print(f'找到{len(status_changes)}条状态变化记录：')
for change in status_changes[:10]:
    print(f'  ID={change[0]}, 姓名={change[2]}, 当前状态={change[3]}, 更新时间={change[4]}')

print('\n2. 岗位聘任信息表：现受聘岗位名称变化')
print('-' * 80)
print('查询条件：updated_at在指定月份')
cursor.execute("""
    SELECT 
        p.id_card,
        p.name,
        p.post_1,
        p.updated_at
    FROM post_appointment_info p
    WHERE p.updated_at >= %s AND p.updated_at < %s
    ORDER BY p.updated_at DESC
""", (f'{report_month}-01', f'{year}-{month+1:02d}-01' if month < 12 else f'{year+1}-01-01'))
post_changes = cursor.fetchall()
print(f'找到{len(post_changes)}条岗位变化记录：')
for change in post_changes[:10]:
    print(f'  姓名={change[1]}, 当前岗位={change[2]}, 更新时间={change[3]}')

print('\n3. 问题：无法知道原来的值')
print('-' * 80)
print('只能知道被更新了，但不知道：')
print('  - 原来的状态是什么？')
print('  - 原来的岗位是什么？')
print('')
print('需要有一个变更历史表来记录每次变化的前后值')

print('\n4. 检查是否有变更历史表')
print('-' * 80)
cursor.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema='public' 
    AND table_type='BASE TABLE'
    AND (table_name LIKE '%history%' OR table_name LIKE '%log%' OR table_name LIKE '%record%')
    ORDER BY table_name
""")
tables = cursor.fetchall()
print(f'历史记录相关的表：')
for table in tables:
    print(f'  - {table[0]}')

print('\n5. 检查personnel_change_records表结构')
print('-' * 80)
cursor.execute("""
    SELECT column_name, data_type
    FROM information_schema.columns
    WHERE table_name='personnel_change_records'
    AND table_schema='public'
    ORDER BY ordinal_position
""")
fields = cursor.fetchall()
print(f'字段：')
for field in fields:
    print(f'  - {field[0]} ({field[1]})')

cursor.close()
conn.close()
