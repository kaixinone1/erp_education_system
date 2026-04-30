import psycopg2
conn = psycopg2.connect(host='localhost', port='5432', database='taiping_education', user='taiping_user', password='taiping_password')
cur = conn.cursor()
cur.execute("UPDATE teacher_basic_info SET employment_status = '在职' WHERE id_card = '42060219771115159X'")
conn.commit()
print('已恢复张峰状态为在职')
conn.close()
