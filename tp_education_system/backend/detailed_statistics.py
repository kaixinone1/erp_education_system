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
print('详细统计各岗位人数：')
print('=' * 80)

print('\n步骤1：获取有绩效工资标签的教师ID')
cursor.execute("SELECT id FROM personal_dict_dictionary WHERE biao_qian = '绩效工资'")
performance_tag = cursor.fetchone()
print(f'绩效工资标签ID: {performance_tag[0]}')

cursor.execute("""
    SELECT DISTINCT employee_id 
    FROM employee_tag_relations 
    WHERE tag_id = %s
""", (performance_tag[0],))
performance_employee_ids = [row[0] for row in cursor.fetchall()]
print(f'有绩效工资标签的教师数量: {len(performance_employee_ids)}')

print('\n步骤2：读取字典映射')
cursor.execute("SELECT id, post FROM dict_dictionary_personal")
dict_mapping = {}
for row in cursor.fetchall():
    dict_mapping[row[0]] = row[1]
print(f'字典映射: {dict_mapping}')

print('\n步骤3：详细统计各岗位人数')
id_list = ','.join([str(x) for x in performance_employee_ids])
cursor.execute(f"""
    SELECT 
        t.id_card,
        t.name,
        p.post_1,
        dict.post
    FROM teacher_basic_info t
    LEFT JOIN post_appointment_info p ON t.id_card = p.id_card
    LEFT JOIN dict_dictionary_personal dict ON CAST(p.post_1 AS INTEGER) = dict.id
    WHERE t.id IN ({id_list})
    ORDER BY dict.post, t.name
""")
results = cursor.fetchall()

print(f'\n总记录数: {len(results)}')

print('\n按岗位分组统计：')
position_stats = {}
for row in results:
    id_card = row[0]
    name = row[1]
    post_1 = row[2]
    post_name = row[3] or '无岗位信息'
    
    if post_name not in position_stats:
        position_stats[post_name] = []
    position_stats[post_name].append(name)

for post_name, names in sorted(position_stats.items()):
    print(f'\n{post_name}: {len(names)}人')
    for name in names[:5]:  # 只显示前5个
        print(f'  - {name}')
    if len(names) > 5:
        print(f'  ... 还有{len(names)-5}人')

print('\n步骤4：检查无岗位信息的人员')
cursor.execute(f"""
    SELECT 
        t.id_card,
        t.name
    FROM teacher_basic_info t
    LEFT JOIN post_appointment_info p ON t.id_card = p.id_card
    WHERE t.id IN ({id_list})
    AND p.id IS NULL
""")
missing = cursor.fetchall()
print(f'有绩效工资标签但无岗位信息的人员: {len(missing)}人')
for m in missing[:10]:
    print(f'  身份证={m[0]}, 姓名={m[1]}')

cursor.close()
conn.close()
