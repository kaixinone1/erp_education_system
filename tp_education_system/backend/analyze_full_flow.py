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
print('整个备注信息流程分析：')
print('=' * 80)

print('\n第一步：检查performance_pay_remarks表的所有数据')
print('-' * 80)
cursor.execute("""
    SELECT id, report_period, remark_type, teacher_id, teacher_name,
           original_status, new_status, original_post, new_post,
           change_category, change_detail, created_at
    FROM performance_pay_remarks
    ORDER BY created_at DESC
    LIMIT 20
""")
rows = cursor.fetchall()
print(f'最近20条记录：')
for row in rows:
    print(f'\nID={row[0]}, 期间={row[1]}, 类型={row[2]}')
    print(f'  教师ID={row[3]}, 姓名={row[4]}')
    print(f'  状态: {row[5]} -> {row[6]}')
    print(f'  岗位: {row[7]} -> {row[8]}')
    print(f'  类别={row[9]}, 详情={row[10]}')
    print(f'  时间={row[11]}')

print('\n\n第二步：检查2026-05期间的记录')
print('-' * 80)
cursor.execute("""
    SELECT id, remark_type, teacher_name, original_status, new_status, 
           original_post, change_category, change_detail
    FROM performance_pay_remarks
    WHERE report_period = '2026-05'
    ORDER BY id
""")
rows = cursor.fetchall()
print(f'2026-05期间共{len(rows)}条记录：')
for row in rows:
    print(f'\nID={row[0]}, 类型={row[1]}, 姓名={row[2]}')
    print(f'  状态: {row[3]} -> {row[4]}')
    print(f'  原岗位: {row[5]}')
    print(f'  类别={row[6]}, 详情={row[7]}')

print('\n\n第三步：分析哪些记录应该输出到备注')
print('-' * 80)
print('根据文档要求，以下情况应该输出：')
print('1. 在职→退休：X级教师退休X人：姓名')
print('2. 退休→在职：X级教师返聘X人：姓名')
print('3. 在职→去世：X级教师死亡X人：姓名')
print('4. 退休→去世：退休教师死亡X人：姓名')
print('5. 在职→调离：X级教师调离X人：姓名')
print('6. 岗位晋升：X级教师晋升X级教师X人：姓名')
print('7. 新增人员：X级教师调入/新录聘X人：姓名')

print('\n当前2026-05期间的记录分析：')
for row in rows:
    id_val, remark_type, name, orig_status, new_status, orig_post, change_category, change_detail = row
    print(f'\nID={id_val}, 类型={remark_type}, 姓名={name}')
    print(f'  状态: {orig_status} -> {new_status}, 原岗位={orig_post}')
    
    if remark_type == 'status_change':
        if orig_status == '在职' and new_status == '退休':
            if orig_post:
                print(f'  ✓ 应该输出: {orig_post}退休1人：{name}')
            else:
                print(f'  ✗ 无法输出: 原岗位为None，应该输出"教师退休1人：{name}"')
        elif orig_status == '退休' and new_status == '在职':
            if orig_post:
                print(f'  ✓ 应该输出: {orig_post}返聘1人：{name}')
            else:
                print(f'  ✗ 无法输出: 原岗位为None，应该输出"教师返聘1人：{name}"')
        elif orig_status == '在职' and new_status == '去世':
            if orig_post:
                print(f'  ✓ 应该输出: {orig_post}死亡1人：{name}')
            else:
                print(f'  ✗ 无法输出: 原岗位为None，应该输出"教师死亡1人：{name}"')
        elif orig_status == '退休' and new_status == '去世':
            print(f'  ✓ 应该输出: 退休教师死亡1人：{name}')
        else:
            print(f'  ? 其他状态变化，需要确认是否输出')
    elif remark_type == 'position_change':
        print(f'  ✓ 岗位变化，应该输出晋升信息')
    elif remark_type == 'new_employee':
        print(f'  ✓ 新增人员，应该输出调入/新录聘信息')

print('\n\n第四步：检查备注信息读取和汇总逻辑')
print('-' * 80)
print('需要检查performance_pay_routes.py中的备注信息读取逻辑')

cursor.close()
conn.close()
