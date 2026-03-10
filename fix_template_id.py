import psycopg2
import json

conn = psycopg2.connect(host='localhost', port='5432', database='taiping_education', user='taiping_user', password='taiping_password')
cur = conn.cursor()

print("=== 当前清单模板 ===")
cur.execute('SELECT id, "清单名称", "任务项列表" FROM business_checklist')
rows = cur.fetchall()
for row in rows:
    print(f"\nID: {row[0]}, 名称: {row[1]}")
    tasks = row[2]
    if isinstance(tasks, str):
        tasks = json.loads(tasks)
    for i, task in enumerate(tasks or []):
        params = task.get('参数', {})
        print(f"  任务{i+1}: {task.get('标题')} - 模板ID: {params.get('template_id')}")

# 更新所有包含 html 后缀的模板ID
print("\n=== 更新模板ID ===")

# 任务1: 职工退休呈报表html -> 职工退休呈报表
cur.execute("""
    UPDATE business_checklist 
    SET "任务项列表" = (
        SELECT jsonb_agg(
            CASE 
                WHEN task->'参数'->>'template_id' = '职工退休呈报表html'
                THEN jsonb_set(task, '{参数,template_id}', '"职工退休呈报表"')
                ELSE task
            END
        )
        FROM jsonb_array_elements("任务项列表") AS task
    )
    WHERE "清单名称" LIKE '%退休%'
""")
print(f"任务1更新: {cur.rowcount} 条")

# 任务3: 带htm后缀的 -> 去掉后缀
cur.execute("""
    UPDATE business_checklist 
    SET "任务项列表" = (
        SELECT jsonb_agg(
            CASE 
                WHEN task->'参数'->>'template_id' LIKE '%.htm%'
                THEN jsonb_set(
                    task, 
                    '{参数,template_id}', 
                    to_jsonb(replace(replace(task->'参数'->>'template_id', '.html', ''), '.htm', ''))
                )
                ELSE task
            END
        )
        FROM jsonb_array_elements("任务项列表") AS task
    )
    WHERE "清单名称" LIKE '%退休%'
""")
print(f"任务3更新: {cur.rowcount} 条")

conn.commit()

print("\n=== 更新后清单 ===")
cur.execute('SELECT id, "清单名称", "任务项列表" FROM business_checklist')
rows = cur.fetchall()
for row in rows:
    print(f"\nID: {row[0]}, 名称: {row[1]}")
    tasks = row[2]
    if isinstance(tasks, str):
        tasks = json.loads(tasks)
    for i, task in enumerate(tasks or []):
        params = task.get('参数', {})
        print(f"  任务{i+1}: {task.get('标题')} - 模板ID: {params.get('template_id')}")

cur.close()
conn.close()
