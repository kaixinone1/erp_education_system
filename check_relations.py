import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port='5432',
    database='taiping_education',
    user='taiping_user',
    password='taiping_password'
)
cursor = conn.cursor()

# 查看关系表记录数
cursor.execute("SELECT COUNT(*) FROM employee_tag_relations")
count = cursor.fetchone()[0]
print(f'employee_tag_relations 表记录数: {count}')

# 查看前20条关系数据
cursor.execute("""
    SELECT 
        r.id,
        r.employee_id,
        t.name as teacher_name,
        t.id_card,
        r.tag_id,
        d.biao_qian as tag_name,
        r.created_at
    FROM employee_tag_relations r
    JOIN teacher_basic_info t ON r.employee_id = t.id
    JOIN personal_dict_dictionary d ON r.tag_id = d.id
    ORDER BY r.id
    LIMIT 20
""")

print('\n前20条关系数据:')
print('=' * 100)
print(f'{"ID":<5} {"教师ID":<8} {"姓名":<10} {"身份证":<20} {"标签ID":<8} {"标签":<15} {"创建时间":<20}')
print('-' * 100)

for row in cursor.fetchall():
    print(f'{row[0]:<5} {row[1]:<8} {row[2]:<10} {row[3]:<20} {row[4]:<8} {row[5]:<15} {str(row[6]):<20}')

# 统计每个教师的标签数量
cursor.execute("""
    SELECT 
        t.name,
        t.id_card,
        COUNT(*) as tag_count
    FROM employee_tag_relations r
    JOIN teacher_basic_info t ON r.employee_id = t.id
    GROUP BY t.id, t.name, t.id_card
    ORDER BY tag_count DESC
    LIMIT 10
""")

print('\n\n标签数量最多的前10位教师:')
print('=' * 60)
print(f'{"姓名":<10} {"身份证":<20} {"标签数量":<10}')
print('-' * 60)
for row in cursor.fetchall():
    print(f'{row[0]:<10} {row[1]:<20} {row[2]:<10}')

# 统计每个标签的教师数量
cursor.execute("""
    SELECT 
        d.biao_qian,
        COUNT(*) as teacher_count
    FROM employee_tag_relations r
    JOIN personal_dict_dictionary d ON r.tag_id = d.id
    GROUP BY d.id, d.biao_qian
    ORDER BY teacher_count DESC
""")

print('\n\n各标签的教师数量统计:')
print('=' * 40)
print(f'{"标签":<20} {"教师数量":<10}')
print('-' * 40)
for row in cursor.fetchall():
    print(f'{row[0]:<20} {row[1]:<10}')

cursor.close()
conn.close()
