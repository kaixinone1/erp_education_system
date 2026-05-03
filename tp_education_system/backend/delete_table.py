import psycopg2
conn = psycopg2.connect(host='localhost', port='5432', database='taiping_education', user='taiping_user', password='taiping_password')
cursor = conn.cursor()

cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'teacher_certificate_info'")
if cursor.fetchone():
    print('表 teacher_certificate_info 存在，正在删除...')
    cursor.execute('DROP TABLE teacher_certificate_info CASCADE')
    conn.commit()
    print('删除成功')
else:
    print('表 teacher_certificate_info 不存在')

cursor.close()
conn.close()