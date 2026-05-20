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
print('按照用户要求的正确流程分析：')
print('=' * 80)

print('\n步骤1：从标签关系管理表获取有"绩效工资"标签的教师')
print('-' * 80)
print('表名：employee_tag_relations (标签关系管理表)')
cursor.execute("SELECT id FROM personal_dict_dictionary WHERE biao_qian = '绩效工资'")
performance_tag = cursor.fetchone()
print(f'绩效工资标签ID: {performance_tag[0] if performance_tag else None}')

if performance_tag:
    cursor.execute("""
        SELECT DISTINCT employee_id 
        FROM employee_tag_relations 
        WHERE tag_id = %s
    """, (performance_tag[0],))
    performance_employee_ids = [row[0] for row in cursor.fetchall()]
    print(f'有绩效工资标签的教师数量: {len(performance_employee_ids)}')

print('\n步骤2：从教师基础信息表获取身份证号码')
print('-' * 80)
print('表名：teacher_basic_info (教师基础信息表)')
cursor.execute("""
    SELECT id, id_card, name, employment_status
    FROM teacher_basic_info
    WHERE id IN ({})
""".format(','.join([str(x) for x in performance_employee_ids]) if performance_employee_ids else '0'))
teachers = cursor.fetchall()
print(f'匹配到的教师数量: {len(teachers)}')

id_cards = [t[1] for t in teachers]
print(f'身份证号码数量: {len(id_cards)}')

print('\n步骤3：从岗位聘任信息表获取岗位信息')
print('-' * 80)
print('表名：post_appointment_info (岗位聘任信息表)')
cursor.execute("""
    SELECT 
        p.id_card,
        p.name,
        p.post_1,
        p.post_level_1
    FROM post_appointment_info p
    WHERE p.id_card IN ({})
    LIMIT 20
""".format(','.join([f"'{x}'" for x in id_cards[:20]]) if id_cards else "''"))
rows = cursor.fetchall()
print(f'岗位信息（前20个）：')
for i, row in enumerate(rows):
    print(f'  {i+1}. 身份证={row[0]}, 姓名={row[1]}, post_1={row[2]}, post_level_1={row[3]}')

print('\n统计post_1字段的值：')
cursor.execute("""
    SELECT 
        p.post_1,
        COUNT(*) as cnt
    FROM post_appointment_info p
    WHERE p.id_card IN ({})
    GROUP BY p.post_1
    ORDER BY cnt DESC
""".format(','.join([f"'{x}'" for x in id_cards]) if id_cards else "''"))
positions = cursor.fetchall()
print(f'post_1字段统计：')
for pos in positions:
    print(f'  {pos[0]}: {pos[1]}人')

print('\n步骤4：从教师个人身份表获取个人身份')
print('-' * 80)
print('表名：teacher_personal_identity (教师个人身份表)')
cursor.execute("""
    SELECT 
        t.id_card,
        t.ge_ren_shen_fen
    FROM teacher_personal_identity t
    WHERE t.id_card IN ({})
    LIMIT 20
""".format(','.join([f"'{x}'" for x in id_cards[:20]]) if id_cards else "''"))
rows = cursor.fetchall()
print(f'个人身份信息（前20个）：')
for i, row in enumerate(rows):
    print(f'  {i+1}. 身份证={row[0]}, 个人身份={row[1]}')

print('\n统计个人身份：')
cursor.execute("""
    SELECT 
        t.ge_ren_shen_fen,
        COUNT(*) as cnt
    FROM teacher_personal_identity t
    WHERE t.id_card IN ({})
    GROUP BY t.ge_ren_shen_fen
    ORDER BY cnt DESC
""".format(','.join([f"'{x}'" for x in id_cards]) if id_cards else "''"))
identities = cursor.fetchall()
print(f'个人身份统计：')
for identity in identities:
    print(f'  {identity[0]}: {identity[1]}人')

cursor.close()
conn.close()
