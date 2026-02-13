#!/usr/bin/env python3
"""分析模板ID的存储和流转"""
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
print("1. 数据库中的文档模板")
print("=" * 70)
cursor.execute("""
    SELECT id, template_id, template_name, file_name, created_at
    FROM document_templates
    ORDER BY created_at DESC
""")
for row in cursor.fetchall():
    print(f"\nID: {row[0]}")
    print(f"  template_id: {row[1]}")
    print(f"  template_name: {row[2]}")
    print(f"  file_name: {row[3]}")
    print(f"  created_at: {row[4]}")

print("\n" + "=" * 70)
print("2. 清单模板中配置的template_id")
print("=" * 70)
cursor.execute("""
    SELECT id, 清单名称, 任务项列表
    FROM checklist_templates
    WHERE 是否有效 = true
""")
for row in cursor.fetchall():
    print(f"\n清单: {row[1]} (ID: {row[0]})")
    tasks = row[2] if row[2] else []
    for task in tasks:
        if task.get('类型') == '填报':
            params = task.get('参数', {})
            template_id = params.get('template_id') or params.get('模板ID')
            if template_id:
                print(f"  任务: {task.get('标题')}")
                print(f"    template_id: {template_id}")

print("\n" + "=" * 70)
print("3. 检查模板文件是否存在")
print("=" * 70)
cursor.execute("SELECT template_id, file_path FROM document_templates")
for row in cursor.fetchall():
    import os
    exists = "✓ 存在" if os.path.exists(row[1]) else "✗ 不存在"
    print(f"{row[0]}: {exists}")

cursor.close()
conn.close()
