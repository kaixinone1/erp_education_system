#!/usr/bin/env python3
import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port=5432,
    database='taiping_education',
    user='taiping_user',
    password='taiping_password'
)
cursor = conn.cursor()

# 先检查表是否存在
cursor.execute("""
    SELECT EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_name = 'teacher_education_records'
    )
""")
exists = cursor.fetchone()[0]

if exists:
    # 删除表及数据
    cursor.execute('DROP TABLE IF EXISTS teacher_education_records CASCADE')
    conn.commit()
    print('教师学历记录表已删除')
else:
    print('教师学历记录表不存在')

cursor.close()
conn.close()
