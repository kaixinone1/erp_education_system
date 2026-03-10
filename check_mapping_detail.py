"""
检查字段映射配置的详细信息
"""
import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port='5432',
    database='taiping_education',
    user='taiping_user',
    password='taiping_password'
)
cursor = conn.cursor()

template_id = '枣阳市机关事业单位养老保险改革过渡期内职务升降退休人员信息申报表htm'

# 获取所有字段映射
cursor.execute("""
    SELECT placeholder_name, intermediate_field
    FROM template_field_mapping
    WHERE template_id = %s AND is_active = true
""", (template_id,))

rows = cursor.fetchall()
print(f'数据库中的字段映射配置（共{len(rows)}条）:\n')

# 提取的占位符
extracted = ['姓名', '性别', '个人编号', '事业管理岗位1', '薪级1', '事业专技岗位2', '薪级2', '事业工勤岗位3', '薪级3', '事业管理岗位4']

# 检查哪些有映射，哪些没有
mapped_names = [row[0] for row in rows]

print('提取的占位符 vs 数据库映射:')
for name in extracted:
    if name in mapped_names:
        idx = mapped_names.index(name)
        print(f'  ✓ {name} -> {rows[idx][1]}')
    else:
        print(f'  ✗ {name} -> 未映射')

print(f'\n数据库中有但提取中没有的:')
for row in rows:
    if row[0] not in extracted:
        print(f'  - {row[0]} -> {row[1]}')

cursor.close()
conn.close()
