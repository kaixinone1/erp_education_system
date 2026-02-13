#!/usr/bin/env python3
"""验证完整流程"""
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
cursor.execute("SELECT template_id, template_name, file_name FROM document_templates")
for row in cursor.fetchall():
    print(f"  template_id: {row[0]}")
    print(f"  template_name: {row[1]}")
    print(f"  file_name: {row[2]}")
    print()

print("=" * 70)
print("2. 清单模板配置 (business_checklist)")
print("=" * 70)
cursor.execute("SELECT 任务项列表 FROM business_checklist WHERE 是否有效 = true")
row = cursor.fetchone()
if row:
    tasks = row[0] or []
    for task in tasks:
        if '填报' in task.get('标题', ''):
            print(f"  任务: {task.get('标题')}")
            params = task.get('参数', {})
            print(f"  参数:")
            for k, v in params.items():
                print(f"    {k}: {v}")
            print()

print("=" * 70)
print("3. 验证文件是否存在")
print("=" * 70)
import os
template_dir = r'd:\erp_thirteen\tp_education_system\backend\templates'
if os.path.exists(template_dir):
    files = os.listdir(template_dir)
    for f in files:
        print(f"  {f}")
else:
    print(f"  目录不存在: {template_dir}")

cursor.close()
conn.close()
