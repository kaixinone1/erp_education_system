#!/usr/bin/env python3
"""检查实际配置"""
import psycopg2
import json

conn = psycopg2.connect(
    host="localhost",
    port="5432",
    database="taiping_education",
    user="taiping_user",
    password="taiping_password"
)
cursor = conn.cursor()

cursor.execute("SELECT 任务项列表 FROM business_checklist WHERE 是否有效 = true")
row = cursor.fetchone()
if row:
    tasks = row[0] or []
    for task in tasks:
        if '退休呈报表' in task.get('标题', ''):
            print(f"任务: {task.get('标题')}")
            print(f"参数: {json.dumps(task.get('参数', {}), ensure_ascii=False, indent=2)}")

cursor.close()
conn.close()
