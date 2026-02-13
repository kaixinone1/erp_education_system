#!/usr/bin/env python3
"""检查当前配置"""
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
print("1. 文档模板")
print("=" * 70)
cursor.execute("SELECT template_id, file_name FROM document_templates")
for row in cursor.fetchall():
    print(f"  {row[0]} -> {row[1]}")

print("\n" + "=" * 70)
print("2. 清单模板配置")
print("=" * 70)
cursor.execute("SELECT 任务项列表 FROM business_checklist WHERE 是否有效 = true")
row = cursor.fetchone()
if row:
    tasks = row[0] or []
    for task in tasks:
        if '填报' in task.get('标题', ''):
            params = task.get('参数', {})
            print(f"\n  任务: {task.get('标题')}")
            for k, v in params.items():
                print(f"    {k}: {v}")

cursor.close()
conn.close()
