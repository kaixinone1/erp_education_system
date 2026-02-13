#!/usr/bin/env python3
"""
调试跳转参数
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

# 获取待办工作
cursor.execute("""
    SELECT id, 教师姓名, 任务项列表
    FROM todo_work_items
    WHERE 清单名称 = '退休教师呈报业务清单'
    ORDER BY id DESC
    LIMIT 1
""")

row = cursor.fetchone()
if row:
    print(f"待办ID: {row[0]}")
    print(f"教师: {row[1]}")
    
    task_items = row[2] if isinstance(row[2], list) else json.loads(row[2]) if row[2] else []
    
    print("\n任务项配置:")
    for task in task_items:
        if task.get('类型') == '内部表':
            print(f"\n  标题: {task.get('标题')}")
            print(f"  目标: {task.get('目标')}")
            params = task.get('参数', {})
            print(f"  template_id: {params.get('template_id', '未配置')}")

cursor.close()
conn.close()
