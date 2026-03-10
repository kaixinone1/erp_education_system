"""
检查数据库中的占位符格式
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

# 检查 template_field_mapping 表中的 placeholder_name
cursor.execute("""
    SELECT placeholder_name
    FROM template_field_mapping
    WHERE template_id = %s AND is_active = true
    LIMIT 5
""", (template_id,))

print('数据库中的 placeholder_name（前5条）:')
for row in cursor.fetchall():
    name = row[0]
    print(f'  原始值: "{name}"')
    print(f'  长度: {len(name)}')
    has_brace = '{' in name
    print(f'  是否包含花括号: {has_brace}')
    print()

cursor.close()
conn.close()
