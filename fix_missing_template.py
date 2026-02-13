#!/usr/bin/env python3
"""修复缺失的模板关联"""
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

# 手动修复"填报《退休呈报表》"任务
# 使用模糊匹配找到正确的模板

print("查找模板...")
cursor.execute("""
    SELECT template_id, file_name, template_name
    FROM document_templates
    WHERE file_name LIKE '%退休%呈报%'
""")

print("\n找到的模板:")
for row in cursor.fetchall():
    print(f"  template_id: {row[0]}")
    print(f"  file_name: {row[1]}")
    print(f"  template_name: {row[2]}")

# 更新清单模板
cursor.execute("""
    SELECT 任务项列表 FROM business_checklist WHERE id = 1
""")
row = cursor.fetchone()
tasks = row[0]

print("\n\n更新前的任务参数:")
for task in tasks:
    if '填报《退休呈报表》' in task.get('标题', ''):
        print(f"  任务: {task.get('标题')}")
        print(f"  参数: {task.get('参数', {})}")
        
        # 更新参数
        task['参数']['template_name'] = '职工退休呈报表.html'
        if 'template_id' in task['参数']:
            del task['参数']['template_id']
        
        print(f"\n  更新后参数: {task.get('参数', {})}")

# 保存更新
cursor.execute("""
    UPDATE business_checklist
    SET 任务项列表 = %s
    WHERE id = 1
""", (json.dumps(tasks),))
conn.commit()

print("\n✓ 已更新清单模板配置")

cursor.close()
conn.close()
