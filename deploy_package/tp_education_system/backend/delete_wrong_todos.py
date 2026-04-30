import psycopg2

conn = psycopg2.connect(host='localhost', port='5432', database='taiping_education', user='taiping_user', password='taiping_password')
cur = conn.cursor()

# 删除错误的待办
cur.execute('DELETE FROM todo_items WHERE id IN (7, 9)')
deleted = cur.rowcount

conn.commit()
print(f'已删除 {deleted} 条待办记录 (ID: 7, 9)')

# 验证
cur.execute('SELECT id, template_id, teacher_name, title FROM todo_items ORDER BY id DESC')
print('删除后剩余待办:')
for row in cur.fetchall():
    print(f'  ID:{row[0]} template_id:{row[1]} 教师:{row[2]}')

conn.close()
