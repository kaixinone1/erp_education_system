#!/usr/bin/env python3
"""检查当前清单配置"""
import psycopg2
import json

DATABASE_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "database": "taiping_education",
    "user": "taiping_user",
    "password": "taiping_password"
}

def check():
    conn = psycopg2.connect(**DATABASE_CONFIG)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, 清单名称, 任务项列表, 触发条件
        FROM business_checklist
        WHERE 清单名称 = '退休教师呈报业务清单'
    """)
    
    row = cursor.fetchone()
    if row:
        print(f"ID: {row[0]}")
        print(f"名称: {row[1]}")
        print(f"触发条件: {row[3]}")
        print("\n当前任务项列表:")
        task_items = row[2] if isinstance(row[2], list) else json.loads(row[2]) if row[2] else []
        for i, task in enumerate(task_items, 1):
            print(f"  {i}. {task}")
    else:
        print("未找到退休教师呈报业务清单")
    
    cursor.close()
    conn.close()

if __name__ == '__main__':
    check()
