#!/usr/bin/env python3
"""
检查API返回的数据
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

# 获取待办工作列表（模拟API查询）
cursor.execute("""
    SELECT id, 清单名称, 教师姓名, 任务项列表
    FROM todo_work_items
    WHERE 状态 = 'pending'
    ORDER BY created_at DESC
    LIMIT 1
""")

row = cursor.fetchone()
if row:
    print(f"待办ID: {row[0]}")
    print(f"清单: {row[1]}")
    print(f"教师: {row[2]}")
    
    task_items = row[3] if isinstance(row[3], list) else json.loads(row[3]) if row[3] else []
    
    print(f"\n任务项数量: {len(task_items)}")
    print("\n完整任务项数据:")
    for i, task in enumerate(task_items, 1):
        print(f"\n{i}. {task.get('标题')}")
        print(f"   类型: {task.get('类型')}")
        print(f"   目标: {task.get('目标')}")
        print(f"   参数: {json.dumps(task.get('参数', {}), ensure_ascii=False)}")

cursor.close()
conn.close()
