#!/usr/bin/env python3
"""修复清单模板中的template_id"""
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

# 获取当前清单模板
cursor.execute("""
    SELECT id, 清单名称, 任务项列表
    FROM business_checklist
    WHERE 是否有效 = true
""")

for row in cursor.fetchall():
    checklist_id = row[0]
    checklist_name = row[1]
    tasks = row[2] if row[2] else []
    
    print(f"\n清单: {checklist_name} (ID: {checklist_id})")
    
    updated = False
    for task in tasks:
        params = task.get('参数', {})
        old_template_id = params.get('template_id')
        
        # 将 职工退休申报表html 改为 职工退休呈报表html
        if old_template_id == '职工退休申报表html':
            params['template_id'] = '职工退休呈报表html'
            updated = True
            print(f"  更新任务: {task.get('标题')}")
            print(f"    {old_template_id} -> 职工退休呈报表html")
    
    if updated:
        # 更新数据库
        cursor.execute("""
            UPDATE business_checklist
            SET 任务项列表 = %s
            WHERE id = %s
        """, (json.dumps(tasks), checklist_id))
        conn.commit()
        print(f"  ✓ 已更新")

cursor.close()
conn.close()
print("\n更新完成!")
