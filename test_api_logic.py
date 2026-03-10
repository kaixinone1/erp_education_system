"""
测试 API 逻辑
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

teacher_id = 293
template_id = '枣阳市机关事业单位养老保险改革过渡期内职务升降退休人员信息申报表htm'

# 1. 查询字段映射
cursor.execute("""
    SELECT placeholder_name, intermediate_table, intermediate_field
    FROM template_field_mapping
    WHERE template_id = %s AND is_active = true
""", (template_id,))

mappings = {}
for row in cursor.fetchall():
    placeholder_name = row[0]
    intermediate_table = row[1] or 'retirement_report_data'
    intermediate_field = row[2]
    mappings[placeholder_name] = {'table': intermediate_table, 'field': intermediate_field}

print(f'获取到 {len(mappings)} 个字段映射')

# 2. 模拟提取的占位符
placeholders = ['{{姓名}}', '{{性别}}', '{{个人编号}}']

# 3. 查询数据
data = {}
for placeholder in placeholders:
    field_name = placeholder.strip('{}')
    print(f'\n处理占位符: {placeholder} -> field_name: {field_name}')
    
    if field_name not in mappings:
        print(f'  错误: {field_name} 不在 mappings 中')
        continue
    
    mapping = mappings[field_name]
    table_name = mapping['table']
    field = mapping['field']
    
    print(f'  表名: {table_name}, 字段: {field}')
    
    try:
        sql = f'SELECT "{field}" FROM "{table_name}" WHERE teacher_id = %s'
        print(f'  SQL: {sql}')
        
        cursor.execute(sql, (teacher_id,))
        row = cursor.fetchone()
        print(f'  查询结果: {row}')
        
        if row and row[0]:
            data[field_name] = row[0]
        else:
            data[field_name] = ''
    except Exception as e:
        print(f'  查询失败: {e}')
        data[field_name] = ''

print(f'\n最终数据: {data}')

cursor.close()
conn.close()
