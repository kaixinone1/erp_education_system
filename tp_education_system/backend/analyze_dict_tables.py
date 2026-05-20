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
print('分析数据库中的字典表：')
print('=' * 80)

print('\n1. 查找所有包含"dict"或"字典"的表')
print('-' * 80)
cursor.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema='public' 
    AND table_type='BASE TABLE'
    AND (table_name LIKE '%dict%' OR table_name LIKE '%字典%')
    ORDER BY table_name
""")
dict_tables = cursor.fetchall()
print(f'找到{len(dict_tables)}个字典表：')
for table in dict_tables:
    table_name = table[0]
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    print(f'  - {table_name} ({count}条数据)')

print('\n2. 分析每个字典表的结构和内容')
print('-' * 80)
for table in dict_tables:
    table_name = table[0]
    print(f'\n表名: {table_name}')
    
    # 获取字段
    cursor.execute("""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name=%s
        AND table_schema='public'
        ORDER BY ordinal_position
    """, (table_name,))
    fields = cursor.fetchall()
    print(f'字段: {[f[0] for f in fields]}')
    
    # 获取示例数据
    cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
    rows = cursor.fetchall()
    print(f'示例数据: {rows}')

print('\n' + '=' * 80)
print('结论：')
print('=' * 80)
print('字典表的特点：')
print('  1. 包含预定义的值（如岗位名称、职务级别等）')
print('  2. 数据量相对较小')
print('  3. 用于其他表的字段关联')
print('')
print('如果数据源表是字典表：')
print('  1. 用户选择目标字段时，应该能看到该字段的所有可能值')
print('  2. 提供下拉菜单或折叠菜单，让用户选择一个或多个值')
print('  3. 保证统计数据精准')

cursor.close()
conn.close()
