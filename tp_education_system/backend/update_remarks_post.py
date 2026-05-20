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
print('更新历史记录，补充岗位信息：')
print('=' * 80)

# 读取字典映射
cursor.execute("SELECT id, post FROM dict_dictionary_personal")
dict_mapping = {}
for row in cursor.fetchall():
    dict_mapping[row[0]] = row[1]

print(f'字典映射: {dict_mapping}')

# 查询所有原岗位为None的记录
cursor.execute("""
    SELECT id, teacher_id, teacher_name, original_status, new_status
    FROM performance_pay_remarks
    WHERE original_post IS NULL
    ORDER BY id
""")
rows = cursor.fetchall()
print(f'\n找到{len(rows)}条原岗位为None的记录')

for row in rows:
    remark_id = row[0]
    teacher_id = row[1]
    teacher_name = row[2]
    
    # 获取教师的身份证号码
    cursor.execute("SELECT id_card FROM teacher_basic_info WHERE id = %s", (teacher_id,))
    id_card_row = cursor.fetchone()
    if id_card_row:
        id_card = id_card_row[0]
        
        # 获取岗位信息
        cursor.execute("SELECT post_1 FROM post_appointment_info WHERE id_card = %s", (id_card,))
        post_row = cursor.fetchone()
        if post_row and post_row[0]:
            post_id = int(post_row[0])
            post_name = dict_mapping.get(post_id, f'未知岗位{post_id}')
            
            # 更新备注记录
            cursor.execute("""
                UPDATE performance_pay_remarks
                SET original_post = %s
                WHERE id = %s
            """, (post_name, remark_id))
            
            print(f'  更新ID={remark_id}, 姓名={teacher_name}, 岗位={post_name}')

conn.commit()
print('\n更新完成！')

# 验证更新结果
print('\n验证更新结果：')
print('-' * 80)
cursor.execute("""
    SELECT id, teacher_name, original_status, new_status, original_post
    FROM performance_pay_remarks
    WHERE report_period = '2026-05'
    ORDER BY id
""")
rows = cursor.fetchall()
for row in rows:
    print(f'  ID={row[0]}, 姓名={row[1]}, {row[2]}->{row[3]}, 原岗位={row[4]}')

cursor.close()
conn.close()
