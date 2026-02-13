#!/usr/bin/env python3
"""检查待办工作表中的 template_id"""
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
print("检查 todo_work_items 表")
print("=" * 70)

cursor.execute("""
    SELECT id, 教师姓名, 任务项列表
    FROM todo_work_items
    WHERE 状态 = 'pending'
""")

for row in cursor.fetchall():
    print(f"\n待办ID: {row[0]}, 教师: {row[1]}")
    tasks = row[2] if row[2] else []
    updated = False
    
    for task in tasks:
        if '填报' in task.get('标题', ''):
            params = task.get('参数', {})
            template_id = params.get('template_id')
            print(f"  任务: {task.get('标题')}")
            print(f"  template_id: {template_id}")
            
            # 检查是否是旧值
            if template_id == '职工退休申报表html':
                print("  ⚠️  还是旧值！需要更新为: 职工退休呈报表html")
                params['template_id'] = '职工退休呈报表html'
                updated = True
            elif template_id == '职工退休呈报表html':
                print("  ✓ 正确")
    
    if updated:
        # 更新数据库
        cursor.execute("""
            UPDATE todo_work_items
            SET 任务项列表 = %s
            WHERE id = %s
        """, (json.dumps(tasks), row[0]))
        conn.commit()
        print("  ✓ 已更新")

cursor.close()
conn.close()
print("\n完成!")
