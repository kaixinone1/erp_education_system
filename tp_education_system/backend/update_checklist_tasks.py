import psycopg2
import json
conn = psycopg2.connect(host='localhost', port='5432', database='taiping_education', user='taiping_user', password='taiping_password')
cur = conn.cursor()

# 把todo_templates的任务项复制到business_checklist

# ID:2 退休到龄提醒 -> template_code: RETIREMENT_REMIND
cur.execute('''
    UPDATE business_checklist 
    SET "任务项列表" = (
        SELECT task_flow FROM todo_templates WHERE template_code = 'RETIREMENT_REMIND'
    )
    WHERE "清单名称" = '退休到龄提醒'
''')

# ID:3 80周岁高龄补贴提醒 -> template_code: OCTOGENARIAN_001
cur.execute('''
    UPDATE business_checklist 
    SET "任务项列表" = (
        SELECT task_flow FROM todo_templates WHERE template_code = 'OCTOGENARIAN_001'
    )
    WHERE "清单名称" = '80周岁高龄补贴提醒'
''')

# ID:4 教师死亡后待办工作 -> template_code: DEATH_001
cur.execute('''
    UPDATE business_checklist 
    SET "任务项列表" = (
        SELECT task_flow FROM todo_templates WHERE template_code = 'DEATH_001'
    )
    WHERE "清单名称" = '教师死亡后待办工作'
''')

conn.commit()

# 验证
cur.execute('SELECT id, "清单名称", "任务项列表" FROM business_checklist')
print('=== business_checklist 任务项 ===')
for row in cur.fetchall():
    print(f'ID:{row[0]} 名称:{row[1]}')
    tasks = row[2]
    if tasks:
        if isinstance(tasks, str):
            tasks = json.loads(tasks)
        print(f'  任务项数: {len(tasks)}')
    else:
        print(f'  任务项: 空')

conn.close()
