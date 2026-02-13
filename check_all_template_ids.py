#!/usr/bin/env python3
"""检查所有表中的 template_id 是否一致"""
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
print("1. 文档模板表 (document_templates)")
print("=" * 70)
cursor.execute("SELECT template_id, template_name FROM document_templates ORDER BY template_id")
doc_templates = {row[0]: row[1] for row in cursor.fetchall()}
for tid, tname in doc_templates.items():
    print(f"  {tid} -> {tname}")

print("\n" + "=" * 70)
print("2. 清单模板表 (business_checklist)")
print("=" * 70)
cursor.execute("SELECT 清单名称, 任务项列表 FROM business_checklist WHERE 是否有效 = true")
for row in cursor.fetchall():
    print(f"\n  清单: {row[0]}")
    tasks = row[1] or []
    for task in tasks:
        if task.get('类型') == '填报':
            params = task.get('参数', {})
            tid = params.get('template_id')
            tname = params.get('template_name')
            status = "✓" if tid in doc_templates else "✗ 不存在"
            print(f"    任务: {task.get('标题')}")
            print(f"    template_id: {tid} {status}")

print("\n" + "=" * 70)
print("3. 待办工作表 (todo_work_items)")
print("=" * 70)
cursor.execute("SELECT id, 教师姓名, 任务项列表 FROM todo_work_items WHERE 状态 = 'pending'")
for row in cursor.fetchall():
    print(f"\n  待办ID: {row[0]}, 教师: {row[1]}")
    tasks = row[2] or []
    for task in tasks:
        if task.get('类型') == '填报':
            params = task.get('参数', {})
            tid = params.get('template_id')
            status = "✓" if tid in doc_templates else "✗ 不存在"
            print(f"    任务: {task.get('标题')}")
            print(f"    template_id: {tid} {status}")

cursor.close()
conn.close()
print("\n" + "=" * 70)
print("检查完成!")
print("=" * 70)
