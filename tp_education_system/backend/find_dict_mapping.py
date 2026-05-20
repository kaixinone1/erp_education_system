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
print('查找post_1字段的字典映射：')
print('=' * 80)

print('\n配置文件显示：')
print('  - 字段名：post_1')
print('  - 中文名：现受聘岗位名称')
print('  - 关联字典表：dict_dictionary_personal')
print('  - 显示字段：post')

print('\n检查dict_dictionary_personal表：')
print('-' * 80)
cursor.execute("""
    SELECT column_name, data_type
    FROM information_schema.columns
    WHERE table_name='dict_dictionary_personal'
    AND table_schema='public'
    ORDER BY ordinal_position
""")
fields = cursor.fetchall()
print(f'字段：')
for field in fields:
    print(f'  - {field[0]} ({field[1]})')

cursor.execute("SELECT * FROM dict_dictionary_personal ORDER BY id")
rows = cursor.fetchall()
print(f'\n数据内容：')
for row in rows:
    print(f'  ID={row[0]}, post={row[1] if len(row) > 1 else None}')

print('\n检查dict_dictionary表：')
print('-' * 80)
cursor.execute("""
    SELECT column_name, data_type
    FROM information_schema.columns
    WHERE table_name='dict_dictionary'
    AND table_schema='public'
    ORDER BY ordinal_position
""")
fields = cursor.fetchall()
print(f'字段：')
for field in fields:
    print(f'  - {field[0]} ({field[1]})')

cursor.execute("SELECT * FROM dict_dictionary ORDER BY id")
rows = cursor.fetchall()
print(f'\n数据内容：')
for row in rows:
    print(f'  {row}')

print('\n检查岗位名称字典：')
print('-' * 80)
cursor.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema='public' 
    AND table_type='BASE TABLE'
    AND table_name LIKE '%岗位%'
    ORDER BY table_name
""")
tables = cursor.fetchall()
print(f'岗位相关表：{[t[0] for t in tables]}')

cursor.close()
conn.close()
