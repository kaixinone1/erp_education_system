"""
检查中间表的字段名
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

# 获取 retirement_report_data 表的所有字段名
cursor.execute("""
    SELECT column_name 
    FROM information_schema.columns 
    WHERE table_name = 'retirement_report_data'
    ORDER BY ordinal_position
""")

print('retirement_report_data 表的所有字段:')
fields = [row[0] for row in cursor.fetchall()]
for field in fields[:20]:
    print(f'  {field}')

# 检查几个关键字段的值
cursor.execute("""
    SELECT 姓名, 性别, 出生日期, 民族, 籍贯
    FROM retirement_report_data
    WHERE teacher_id = 273
""")

row = cursor.fetchone()
if row:
    print(f'\nteacher_id = 273 的关键字段值:')
    print(f'  姓名: {row[0]}')
    print(f'  性别: {row[1]}')
    print(f'  出生日期: {row[2]}')
    print(f'  民族: {row[3]}')
    print(f'  籍贯: {row[4]}')

cursor.close()
conn.close()
