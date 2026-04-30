import psycopg2
import json

conn = psycopg2.connect(host='localhost', port='5432', database='taiping_education', user='taiping_user', password='taiping_password')
cur = conn.cursor()

# 为现有待办生成历史记录
cur.execute('''
    SELECT id, teacher_id, teacher_name, template_id, business_type, title, description, status, task_items, created_at
    FROM todo_items
''')

count = 0
for row in cur.fetchall():
    todo_id, teacher_id, teacher_name, template_id, business_type, title, description, status, task_items, created_at = row
    
    # task_items需要转成JSON字符串
    task_items_json = json.dumps(task_items) if task_items else None
    
    # 插入历史记录
    cur.execute('''
        INSERT INTO todo_history (
            todo_id, teacher_id, teacher_name, template_code, business_type,
            title, description, status, task_items, created_at
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ''', (
        todo_id, teacher_id, teacher_name, template_id, business_type,
        title, description, status, task_items_json, created_at
    ))
    count += 1

conn.commit()
print(f'已为 {count} 条待办生成历史记录')

# 验证
cur.execute('SELECT COUNT(*) FROM todo_history')
print(f'待办历史总记录数: {cur.fetchone()[0]}')

conn.close()
