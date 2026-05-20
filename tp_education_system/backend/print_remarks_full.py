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
print('performance_pay_remarks表全部信息：')
print('=' * 80)

cursor.execute("""
    SELECT id, report_period, remark_type, teacher_id, teacher_name,
           original_status, new_status, original_post, new_post,
           change_category, change_detail, created_at
    FROM performance_pay_remarks
    ORDER BY id
""")
rows = cursor.fetchall()

print(f'\n总记录数: {len(rows)}')

for row in rows:
    print('\n' + '=' * 80)
    print(f'ID = {row[0]}')
    print(f'报告期间 = {row[1]}')
    print(f'备注类型 = {row[2]}')
    print(f'教师ID = {row[3]}')
    print(f'教师姓名 = {row[4]}')
    print(f'原状态 = {row[5]}')
    print(f'新状态 = {row[6]}')
    print(f'原岗位 = {row[7]}')
    print(f'新岗位 = {row[8]}')
    print(f'变化类别 = {row[9]}')
    print(f'变化详情 = {row[10]}')
    print(f'创建时间 = {row[11]}')

print('\n' + '=' * 80)
print('2026-05期间的记录：')
print('=' * 80)

cursor.execute("""
    SELECT id, teacher_name, original_status, new_status, original_post, change_detail
    FROM performance_pay_remarks
    WHERE report_period = '2026-05'
    ORDER BY id
""")
rows = cursor.fetchall()

print(f'\n2026-05期间记录数: {len(rows)}')

for row in rows:
    print(f'\nID={row[0]}, 姓名={row[1]}')
    print(f'  状态变化: {row[2]} -> {row[3]}')
    print(f'  原岗位: {row[4]}')
    print(f'  变化详情: {row[5]}')

print('\n' + '=' * 80)
print('分析：哪些记录应该输出到备注信息？')
print('=' * 80)

print('\n根据文档要求，以下情况应该输出：')
print('1. 在职→调离：X级教师调离X人：姓名')
print('2. 在职→调出：X级教师调出X人：姓名')
print('3. 在职→离职：X级教师离职X人：姓名')
print('4. 退休→去世：退休教师死亡X人：姓名')
print('5. 在职→去世：X级教师死亡X人：姓名')
print('6. 在职→辞职：X级教师辞职X人：姓名')
print('7. 在职→退休：X级教师退休X人：姓名')
print('8. 退休→在职：X级教师返聘X人：姓名')

print('\n当前2026-05期间的记录分析：')
for row in rows:
    id_val, name, orig_status, new_status, orig_post, change_detail = row
    print(f'\nID={id_val}, 姓名={name}, {orig_status}->{new_status}, 原岗位={orig_post}')
    
    if orig_status == '在职' and new_status == '退休':
        if orig_post:
            print(f'  ✓ 应该输出: {orig_post}退休1人：{name}')
        else:
            print(f'  ✗ 无法输出: 原岗位为None')
    elif orig_status == '退休' and new_status == '在职':
        if orig_post:
            print(f'  ✓ 应该输出: {orig_post}返聘1人：{name}')
        else:
            print(f'  ✗ 无法输出: 原岗位为None')
    elif orig_status == '在职' and new_status == '去世':
        if orig_post:
            print(f'  ✓ 应该输出: {orig_post}死亡1人：{name}')
        else:
            print(f'  ✗ 无法输出: 原岗位为None')
    else:
        print(f'  ? 其他情况，需要确认是否输出')

cursor.close()
conn.close()
