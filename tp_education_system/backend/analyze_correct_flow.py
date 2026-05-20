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
print('按照用户说明的正确流程分析：')
print('=' * 80)

print('\n步骤1：从标签关系管理表获取有"绩效工资"标签的教师')
print('-' * 80)
cursor.execute("""
    SELECT id FROM personal_dict_dictionary WHERE biao_qian = '绩效工资'
""")
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

print('\n步骤2：与教师基础信息表比对，确定统计口径')
print('-' * 80)
cursor.execute("""
    SELECT id, id_card, name, employment_status
    FROM teacher_basic_info
    WHERE id IN ({})
    LIMIT 10
""".format(','.join([str(x) for x in performance_employee_ids[:20]]) if performance_employee_ids else '0'))
teachers = cursor.fetchall()
print(f'示例教师（前10个）：')
for t in teachers:
    print(f'  ID={t[0]}, 身份证={t[1]}, 姓名={t[2]}, 状态={t[3]}')

print('\n步骤3：从岗位聘任信息表获取岗位信息')
print('-' * 80)
cursor.execute("""
    SELECT 
        t.id_card,
        t.name,
        p.post_1,
        p.post_level_1,
        i.post_2
    FROM teacher_basic_info t
    LEFT JOIN post_appointment_info p ON t.id_card = p.id_card
    LEFT JOIN info i ON t.id_card = i.id_card
    WHERE t.id IN ({})
    LIMIT 20
""".format(','.join([str(x) for x in performance_employee_ids[:20]]) if performance_employee_ids else '0'))
rows = cursor.fetchall()
print(f'岗位信息（前20个）：')
for i, row in enumerate(rows):
    print(f'  {i+1}. 身份证={row[0]}, 姓名={row[1]}, post_1={row[2]}, post_level_1={row[3]}, post_2={row[4]}')

print('\n步骤4：统计各岗位人数')
print('-' * 80)
cursor.execute("""
    SELECT 
        i.post_2,
        COUNT(*) as cnt
    FROM teacher_basic_info t
    LEFT JOIN info i ON t.id_card = i.id_card
    WHERE t.id IN ({})
    AND i.post_2 IS NOT NULL AND i.post_2 != ''
    GROUP BY i.post_2
    ORDER BY cnt DESC
""".format(','.join([str(x) for x in performance_employee_ids]) if performance_employee_ids else '0'))
positions = cursor.fetchall()
print(f'各岗位人数统计：')
for pos in positions:
    print(f'  {pos[0]}: {pos[1]}人')

print('\n步骤5：从绩效工资标准字典获取工资标准')
print('-' * 80)
cursor.execute("SELECT post_1, month_performance_salary FROM dict_salary_dictionary")
standards = cursor.fetchall()
print(f'工资标准：')
for std in standards:
    print(f'  {std[0]}: {std[1]}元')

cursor.close()
conn.close()
