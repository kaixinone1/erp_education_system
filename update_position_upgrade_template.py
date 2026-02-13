#!/usr/bin/env python3
"""
为职务升级表任务配置template_id
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

# 获取当前清单模板
cursor.execute("""
    SELECT id, 清单名称, 任务项列表
    FROM business_checklist
    WHERE 清单名称 = '退休教师呈报业务清单'
""")

row = cursor.fetchone()
if row:
    checklist_id = row[0]
    task_items = row[2] if isinstance(row[2], list) else json.loads(row[2]) if row[2] else []
    
    print(f"找到清单: {row[1]} (ID: {checklist_id})")
    
    # 为职务升级表任务添加template_id
    for task in task_items:
        if task.get('标题') == '填报《职务升级表》':
            print(f"\n更新任务: {task['标题']}")
            print(f"原参数: {task.get('参数', {})}")
            
            # 添加template_id到参数中（暂时使用职工退休申报表模板）
            if '参数' not in task:
                task['参数'] = {}
            task['参数']['template_id'] = '职工退休申报表html'
            
            print(f"新参数: {task['参数']}")
    
    # 更新数据库
    cursor.execute("""
        UPDATE business_checklist
        SET 任务项列表 = %s,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = %s
    """, (json.dumps(task_items), checklist_id))
    
    conn.commit()
    print("\n✅ 清单模板更新成功！")
else:
    print("❌ 未找到清单模板")

cursor.close()
conn.close()
