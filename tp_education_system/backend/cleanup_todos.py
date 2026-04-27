import psycopg2
conn = psycopg2.connect(host='localhost', port='5432', database='taiping_education', user='taiping_user', password='taiping_password')
cur = conn.cursor()

# 删除用错误模板创建的待办
cur.execute("DELETE FROM todo_items WHERE template_id = 'RETIREMENT_APPROVAL'")
deleted = cur.rowcount

conn.commit()
print(f'已删除 {deleted} 条错误的待办')

# 查看当前待办
cur.execute('SELECT id, teacher_name, template_id, status FROM todo_items ORDER BY id DESC')
print('\n当前待办:')
for row in cur.fetchall():
    print(f'  ID:{row[0]} 教师:{row[1]} 模板:{row[2]} 状态:{row[3]}')

conn.close()
