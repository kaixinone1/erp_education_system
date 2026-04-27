#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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

print("=" * 60)
print("查询 business_checklist 表中的清单模板")
print("=" * 60)

cursor.execute('''
    SELECT id, 清单名称, 触发条件, 任务项列表, 是否有效
    FROM business_checklist
    ORDER BY id
''')

rows = cursor.fetchall()
print(f"\n共有 {len(rows)} 个清单模板:\n")

for row in rows:
    print(f"ID: {row[0]}")
    print(f"清单名称: {row[1]}")
    print(f"是否有效: {row[4]}")

    if row[2]:
        try:
            trigger = json.loads(row[2]) if isinstance(row[2], str) else row[2]
            print(f"触发条件: {trigger}")
        except:
            print(f"触发条件: {row[2]}")

    if row[3]:
        try:
            tasks = json.loads(row[3]) if isinstance(row[3], str) else row[3]
            if isinstance(tasks, list):
                print(f"任务数量: {len(tasks)}")
                for i, task in enumerate(tasks):
                    title = task.get('标题', '未命名')
                    task_type = task.get('类型', 'N/A')
                    target = task.get('目标', 'N/A')
                    print(f"  {i+1}. {title} (类型:{task_type}, 目标:{target})")
            else:
                print(f"任务项列表: {tasks}")
        except Exception as e:
            print(f"任务项列表: 解析失败 - {e}")
            print(f"  原始数据: {row[3][:200]}...")
    else:
        print("任务项列表: 无")

    print("-" * 40)

cursor.close()
conn.close()
