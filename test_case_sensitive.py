"""
测试 PostgreSQL 大小写敏感问题
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

# 测试1: 不加引号
try:
    cursor.execute("SELECT 姓名 FROM retirement_report_data WHERE teacher_id = %s", (teacher_id,))
    row = cursor.fetchone()
    print(f'不加引号: {row}')
except Exception as e:
    print(f'不加引号失败: {e}')

# 测试2: 加双引号
try:
    cursor.execute('SELECT "姓名" FROM "retirement_report_data" WHERE teacher_id = %s', (teacher_id,))
    row = cursor.fetchone()
    print(f'加双引号: {row}')
except Exception as e:
    print(f'加双引号失败: {e}')

cursor.close()
conn.close()
