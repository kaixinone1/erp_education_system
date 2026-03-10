import psycopg2
import json

conn = psycopg2.connect(
    host='localhost',
    port='5432',
    database='taiping_education',
    user='taiping_user',
    password='taiping_password'
)
cursor = conn.cursor()

# 获取教师导入数据
cursor.execute("""
    SELECT data_json FROM teacher_import_data 
    WHERE teacher_id = 293 AND data_source = '基本信息'
""")

row = cursor.fetchone()
if row:
    data = json.loads(row[0])
    print('教师数据中的字段值:')
    for key, value in data.items():
        print(f'  {key}: {repr(value)} (类型: {type(value).__name__})')
else:
    print('未找到教师数据')

cursor.close()
conn.close()
