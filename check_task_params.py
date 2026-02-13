#!/usr/bin/env python3
"""检查任务参数配置"""
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

print("=" * 70)
print("检查清单模板任务参数")
print("=" * 70)

cursor.execute("""
    SELECT id, 清单名称, 任务项列表
    FROM business_checklist
    WHERE 是否有效 = true
""")

for row in cursor.fetchall():
    print(f"\n清单: {row[1]} (ID: {row[0]})")
    tasks = row[2] if row[2] else []
    
    for task in tasks:
        if '填报' in task.get('标题', ''):
            print(f"\n  任务: {task.get('标题')}")
            params = task.get('参数', {})
            print(f"  参数:")
            for k, v in params.items():
                print(f"    {k}: {v}")

cursor.close()
conn.close()
