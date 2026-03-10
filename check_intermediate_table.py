"""
检查中间表数据
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

# 检查 teacher_id = 273 的数据是否存在
cursor.execute("""
    SELECT teacher_id, 姓名, 性别, 出生日期
    FROM retirement_report_data
    WHERE teacher_id = 273
""")

row = cursor.fetchone()
if row:
    print(f'找到 teacher_id = 273 的数据:')
    print(f'  teacher_id: {row[0]}')
    print(f'  姓名: {row[1]}')
    print(f'  性别: {row[2]}')
    print(f'  出生日期: {row[3]}')
else:
    print('未找到 teacher_id = 273 的数据')
    
    # 检查有哪些 teacher_id 有数据
    cursor.execute("""
        SELECT teacher_id, 姓名
        FROM retirement_report_data
        LIMIT 5
    """)
    print('\n中间表中的前5条数据:')
    for row in cursor.fetchall():
        print(f'  teacher_id: {row[0]}, 姓名: {row[1]}')

cursor.close()
conn.close()
