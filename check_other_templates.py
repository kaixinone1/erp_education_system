import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port='5432',
    database='taiping_education',
    user='taiping_user',
    password='taiping_password'
)
cursor = conn.cursor()

# 检查所有模板的字段映射配置
cursor.execute("""
    SELECT template_id, COUNT(*) as mapping_count
    FROM template_field_mapping
    GROUP BY template_id
    ORDER BY mapping_count DESC
""")

print('所有模板的字段映射配置:')
for row in cursor.fetchall():
    print(f'  模板: {row[0]}, 映射数: {row[1]}')

# 检查 teacher_import_data 表中是否有教师 293 的数据
cursor.execute("""
    SELECT field_name, value FROM teacher_import_data
    WHERE teacher_id = 293 AND data_source = '基本信息'
    LIMIT 10
""")

print('\nteacher_import_data 表中教师 293 的数据（前10条）:')
rows = cursor.fetchall()
if rows:
    for row in rows:
        print(f'  {row[0]}: {row[1]}')
else:
    print('  无数据')

cursor.close()
conn.close()
