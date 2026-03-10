"""
直接测试查询逻辑
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
table_name = 'retirement_report_data'
field = '姓名'

# 构建SQL
sql = f"SELECT {field} FROM {table_name} WHERE teacher_id = %s"
print(f'SQL: {sql}')
print(f'参数: ({teacher_id},)')

# 执行查询
cursor.execute(sql, (teacher_id,))
row = cursor.fetchone()
print(f'查询结果: {row}')

if row and row[0]:
    print(f'数据: {row[0]}')
else:
    print('无数据')

cursor.close()
conn.close()
