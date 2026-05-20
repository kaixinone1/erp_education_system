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
print('问题分析：')
print('=' * 80)

print('\n2026-05期间的6条记录：')
print('-' * 80)
print('ID=4: 李恩源, 在职->退休, 原岗位=二级教师')
print('ID=5: 李恩源, 退休->在职, 原岗位=二级教师')
print('ID=6: 王治乐, 去世->在职, 原岗位=None')
print('ID=7: 王治乐, 在职->去世, 原岗位=None')
print('ID=8: 郑本超, 去世->在职, 原岗位=None')
print('ID=9: 郑本超, 在职->去世, 原岗位=None')

print('\n问题：')
print('-' * 80)
print('王治乐和郑本超的原岗位都是None，无法生成正确的备注格式')

print('\n检查王治乐和郑本超的详细信息：')
print('-' * 80)

for name in ['王治乐', '郑本超']:
    print(f'\n{name}：')
    
    # 获取教师信息
    cursor.execute("""
        SELECT id, id_card, name, employment_status
        FROM teacher_basic_info
        WHERE name = %s
    """, (name,))
    row = cursor.fetchone()
    if row:
        teacher_id = row[0]
        id_card = row[1]
        print(f'  教师ID={teacher_id}, 身份证={id_card}, 当前状态={row[3]}')
        
        # 检查个人身份
        cursor.execute("""
            SELECT ge_ren_shen_fen
            FROM teacher_personal_identity
            WHERE id_card = %s
        """, (id_card,))
        identity_row = cursor.fetchone()
        if identity_row:
            print(f'  个人身份={identity_row[0]}')
        
        # 检查岗位聘任信息
        cursor.execute("""
            SELECT post_1
            FROM post_appointment_info
            WHERE id_card = %s
        """, (id_card,))
        post_row = cursor.fetchone()
        if post_row:
            print(f'  岗位聘任信息：post_1={post_row[0]}')
        else:
            print(f'  岗位聘任信息：无记录')
        
        # 检查info表
        cursor.execute("""
            SELECT post_2
            FROM info
            WHERE id_card = %s
        """, (id_card,))
        info_row = cursor.fetchone()
        if info_row:
            print(f'  info表：post_2={info_row[0]}')
        else:
            print(f'  info表：无记录')

print('\n' + '=' * 80)
print('结论：')
print('=' * 80)
print('王治乐和郑本超：')
print('  - 在教师基础信息表中')
print('  - 但不在岗位聘任信息表中')
print('  - 也不在info表中')
print('  - 所以无法获取岗位信息')
print('')
print('可能的原因：')
print('  1. 这两个人是退休人员，没有岗位聘任信息')
print('  2. 或者数据导入时缺少了他们的岗位信息')
print('')
print('解决方案：')
print('  1. 检查这两个人是否应该有岗位信息')
print('  2. 如果是退休人员，可以标记为"退休教师"')
print('  3. 如果没有岗位信息，可以在备注中显示"教师死亡X人：姓名"')

cursor.close()
conn.close()
