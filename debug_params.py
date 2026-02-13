#!/usr/bin/env python3
"""调试任务参数"""
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
            print("任务标题:", task.get('标题'))
            print("参数:")
            params = task.get('参数', {})
            print(json.dumps(params, ensure_ascii=False, indent=2))
            
            # 检查字段
            print("\n字段检查:")
            print(f"  template_name: {params.get('template_name')}")
            print(f"  template_id: {params.get('template_id')}")
            print(f"  模板ID: {params.get('模板ID')}")

cursor.close()
conn.close()
