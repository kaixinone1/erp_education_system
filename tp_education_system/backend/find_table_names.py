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
print('查找主菜单对应的数据库表名：')
print('=' * 80)

print('\n1. 主菜单--系统管理--标签关系管理表')
print('-' * 80)
cursor.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema='public' 
    AND table_type='BASE TABLE'
    AND (table_name LIKE '%tag%' OR table_name LIKE '%标签%')
    ORDER BY table_name
""")
tables = cursor.fetchall()
print(f'找到 {len(tables)} 个相关表：')
for table in tables:
    cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
    count = cursor.fetchone()[0]
    print(f'  - {table[0]} ({count}条数据)')

print('\n2. 主菜单--人事管理--教师管理--教师基础信息表')
print('-' * 80)
cursor.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema='public' 
    AND table_type='BASE TABLE'
    AND (table_name LIKE '%teacher_basic%' OR table_name LIKE '%教师基础%')
    ORDER BY table_name
""")
tables = cursor.fetchall()
print(f'找到 {len(tables)} 个相关表：')
for table in tables:
    cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
    count = cursor.fetchone()[0]
    print(f'  - {table[0]} ({count}条数据)')

print('\n3. 主菜单--人事管理--教师管理--岗位聘任信息表')
print('-' * 80)
cursor.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema='public' 
    AND table_type='BASE TABLE'
    AND (table_name LIKE '%post_appointment%' OR table_name LIKE '%岗位聘任%')
    ORDER BY table_name
""")
tables = cursor.fetchall()
print(f'找到 {len(tables)} 个相关表：')
for table in tables:
    cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
    count = cursor.fetchone()[0]
    print(f'  - {table[0]} ({count}条数据)')

print('\n4. 主菜单--人事管理--教师管理--教师个人身份表')
print('-' * 80)
cursor.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema='public' 
    AND table_type='BASE TABLE'
    AND (table_name LIKE '%personal_identity%' OR table_name LIKE '%个人身份%')
    ORDER BY table_name
""")
tables = cursor.fetchall()
print(f'找到 {len(tables)} 个相关表：')
for table in tables:
    cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
    count = cursor.fetchone()[0]
    print(f'  - {table[0]} ({count}条数据)')

print('\n5. 检查info表是什么')
print('-' * 80)
cursor.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema='public' 
    AND table_type='BASE TABLE'
    AND table_name='info'
""")
if cursor.fetchone():
    cursor.execute("SELECT COUNT(*) FROM info")
    count = cursor.fetchone()[0]
    print(f'  - info表存在，有{count}条数据')
    cursor.execute("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name='info'
        AND table_schema='public'
        ORDER BY ordinal_position
    """)
    fields = cursor.fetchall()
    print(f'  - 字段：{[f[0] for f in fields]}')
else:
    print('  - info表不存在')

cursor.close()
conn.close()
