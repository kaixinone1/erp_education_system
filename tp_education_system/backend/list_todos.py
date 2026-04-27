import psycopg2
import json

conn = psycopg2.connect(host='localhost', port='5432', database='taiping_education', user='taiping_user', password='taiping_password')
cur = conn.cursor()

# 查看所有待办
cur.execute('SELECT id, template_id, teacher_name, title, status FROM todo_items ORDER BY id DESC')
print('=== todo_items 表中的待办 ===')
for row in cur.fetchall():
    print(f'ID:{row[0]} template_id:{row[1]} 教师:{row[2]} 标题:{str(row[3])[:30]} 状态:{row[4]}')

print()
# 查看最新待办的任务项
cur.execute('SELECT id, task_items FROM todo_items ORDER BY id DESC LIMIT 1')
row = cur.fetchone()
if row:
    print(f'=== 最新待办(ID:{row[0]})的任务项 ===')
    tasks = row[1]
    if tasks:
        if isinstance(tasks, str):
            tasks = json.loads(tasks)
        for t in tasks:
            print(f'  {t.get("序号")}. {t.get("标题")} ({t.get("类型")})')

conn.close()
