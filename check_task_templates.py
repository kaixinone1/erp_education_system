#!/usr/bin/env python3
"""
检查清单模板中各任务的template_id配置
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

# 获取清单模板
cursor.execute("""
    SELECT id, 清单名称, 任务项列表
    FROM business_checklist
    WHERE 清单名称 = '退休教师呈报业务清单'
""")

row = cursor.fetchone()
if row:
    task_items = row[2] if isinstance(row[2], list) else json.loads(row[2]) if row[2] else []
    
    print("=== 清单模板任务配置 ===\n")
    for task in task_items:
        print(f"任务: {task.get('标题')}")
        print(f"  类型: {task.get('类型')}")
        print(f"  目标: {task.get('目标')}")
        params = task.get('参数', {})
        if isinstance(params, dict):
            print(f"  template_id: {params.get('template_id', '未配置')}")
        print()

cursor.close()
conn.close()
