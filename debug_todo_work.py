#!/usr/bin/env python3
"""
调试待办工作任务项
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

# 获取待办工作列表
cursor.execute("""
    SELECT id, 清单名称, 教师姓名, 任务项列表
    FROM todo_work_items
    ORDER BY id DESC
    LIMIT 3
""")

print("=== 待办工作详情 ===\n")
for row in cursor.fetchall():
    print(f"待办ID: {row[0]}")
    print(f"清单: {row[1]}")
    print(f"教师: {row[2]}")
    
    task_items = row[3] if isinstance(row[3], list) else json.loads(row[3]) if row[3] else []
    print(f"\n任务项数量: {len(task_items)}")
    
    for i, task in enumerate(task_items[:2], 1):  # 只显示前2个
        print(f"\n  任务{i}:")
        print(f"    标题: {task.get('标题')}")
        print(f"    参数: {task.get('参数')}")
    print()

cursor.close()
conn.close()
