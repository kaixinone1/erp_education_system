#!/usr/bin/env python3
"""再次检查数据库配置"""
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
print("检查清单模板中的 template_id")
print("=" * 70)

cursor.execute("SELECT 任务项列表 FROM business_checklist WHERE 是否有效 = true")
row = cursor.fetchone()
if row:
    tasks = row[0] or []
    for task in tasks:
        if '退休' in task.get('标题', ''):
            print(f"\n任务: {task.get('标题')}")
            params = task.get('参数', {})
            template_id = params.get('template_id')
            print(f"  template_id: {template_id}")
            
            # 检查是否是旧值
            if template_id == '职工退休申报表html':
                print("  ⚠️  还是旧值！需要更新为: 职工退休呈报表html")
                params['template_id'] = '职工退休呈报表html'
                # 更新数据库
                cursor.execute(
                    "UPDATE business_checklist SET 任务项列表 = %s WHERE 是否有效 = true",
                    (json.dumps(tasks),)
                )
                conn.commit()
                print("  ✓ 已更新")
            elif template_id == '职工退休呈报表html':
                print("  ✓ 正确")

cursor.close()
conn.close()
