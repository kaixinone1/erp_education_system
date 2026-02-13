#!/usr/bin/env python3
"""
检查清单模板表结构
"""
import sys
sys.path.insert(0, r'd:\erp_thirteen\tp_education_system\backend')

import psycopg2
import json

def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        port="5432",
        database="taiping_education",
        user="taiping_user",
        password="taiping_password"
    )

conn = get_db_connection()
cursor = conn.cursor()

# 检查 business_checklist 表结构
cursor.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = 'business_checklist'
    ORDER BY ordinal_position
""")

print("=== business_checklist 表结构 ===\n")
for row in cursor.fetchall():
    print(f"  {row[0]}: {row[1]}")

# 查看一个清单模板的任务项示例
cursor.execute("""
    SELECT id, 清单名称, 任务项列表
    FROM business_checklist
    WHERE 是否有效 = true
    LIMIT 1
""")

print("\n=== 清单模板示例 ===\n")
row = cursor.fetchone()
if row:
    print(f"ID: {row[0]}")
    print(f"名称: {row[1]}")
    task_items = row[2] if isinstance(row[2], list) else json.loads(row[2]) if row[2] else []
    print(f"\n任务项列表:")
    for i, task in enumerate(task_items, 1):
        print(f"\n  任务{i}:")
        for key, value in task.items():
            print(f"    {key}: {value}")

cursor.close()
conn.close()
