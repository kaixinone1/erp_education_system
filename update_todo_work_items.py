#!/usr/bin/env python3
"""
更新待办工作任务项，添加template_id
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

# 获取最新的清单模板
cursor.execute("""
    SELECT 任务项列表
    FROM business_checklist
    WHERE 清单名称 = '退休教师呈报业务清单'
""")

template_row = cursor.fetchone()
if not template_row:
    print("❌ 未找到清单模板")
    cursor.close()
    conn.close()
    exit()

template_tasks = template_row[0] if isinstance(template_row[0], list) else json.loads(template_row[0]) if template_row[0] else []

# 创建一个映射，用于快速查找模板中的任务参数
template_params_map = {}
for task in template_tasks:
    key = (task.get('标题'), task.get('目标'))
    template_params_map[key] = task.get('参数', {})

print(f"模板任务项数量: {len(template_tasks)}")

# 获取所有待办工作
cursor.execute("""
    SELECT id, 教师姓名, 任务项列表
    FROM todo_work_items
    WHERE 清单名称 = '退休教师呈报业务清单'
""")

todo_list = cursor.fetchall()
print(f"\n待办工作数量: {len(todo_list)}")

updated_count = 0

for todo in todo_list:
    todo_id = todo[0]
    teacher_name = todo[1]
    task_items = todo[2] if isinstance(todo[2], list) else json.loads(todo[2]) if todo[2] else []
    
    modified = False
    
    for task in task_items:
        task_title = task.get('标题')
        task_target = task.get('目标')
        key = (task_title, task_target)
        
        # 如果模板中有这个任务的参数，就更新
        if key in template_params_map:
            template_params = template_params_map[key]
            if 'template_id' in template_params:
                if '参数' not in task:
                    task['参数'] = {}
                task['参数']['template_id'] = template_params['template_id']
                modified = True
                print(f"  更新任务: {task_title} -> template_id: {template_params['template_id']}")
    
    if modified:
        # 更新数据库
        cursor.execute("""
            UPDATE todo_work_items
            SET 任务项列表 = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """, (json.dumps(task_items), todo_id))
        updated_count += 1
        print(f"✅ 已更新待办: {teacher_name} (ID: {todo_id})")

conn.commit()
print(f"\n总共更新了 {updated_count} 个待办工作")

cursor.close()
conn.close()
