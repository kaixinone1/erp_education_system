#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清理到龄退休提醒模板
只保留正确的配置，删除其他混乱的模板
"""
import psycopg2
import json

conn = psycopg2.connect(
    host='localhost',
    port='5432',
    database='taiping_education',
    user='taiping_user',
    password='taiping_password'
)
cursor = conn.cursor()

print("=" * 70)
print("清理到龄退休提醒模板")
print("=" * 70)

# 1. 查看当前所有到龄退休相关的模板
print("\n1. 当前所有到龄退休相关模板：")
cursor.execute('''
    SELECT id, template_code, template_name, business_type, task_flow
    FROM todo_templates
    WHERE template_code LIKE '%RETIREMENT%' 
       OR template_name LIKE '%退休%'
       OR business_type LIKE '%retirement%'
    ORDER BY id
''')

rows = cursor.fetchall()
print(f"找到 {len(rows)} 个模板\n")

for row in rows:
    print(f"ID: {row[0]}")
    print(f"模板编号: {row[1]}")
    print(f"模板名称: {row[2]}")
    print(f"业务类型: {row[3]}")
    if row[4]:
        try:
            tasks = json.loads(row[4]) if isinstance(row[4], str) else row[4]
            if isinstance(tasks, list):
                print(f"任务数量: {len(tasks)}")
                for i, task in enumerate(tasks[:2]):
                    print(f"  - {task.get('title', task.get('标题', '未命名'))}")
        except:
            pass
    print("-" * 50)

# 2. 删除错误的模板，只保留正确的RETIREMENT_REMIND
print("\n2. 删除错误的模板...")

# 要删除的模板编号（保留RETIREMENT_REMIND）
templates_to_delete = [
    'RETIREMENT_APPROVAL',  # 错误的8个未命名任务模板
    'RETIREMENT_001',       # 退休呈报业务清单（这是退休审批用的，不是提醒）
]

for template_code in templates_to_delete:
    cursor.execute('''
        DELETE FROM todo_templates
        WHERE template_code = %s
    ''', (template_code,))
    print(f"  已删除模板: {template_code}")

# 3. 更新RETIREMENT_REMIND模板为正确的配置
print("\n3. 更新RETIREMENT_REMIND模板为正确配置...")

# 正确的任务配置（来自旧版）
correct_task = {
    "标题": "请为{教师姓名}办理退休手续",
    "类型": "退休处理",
    "目标": "retirement_processing",
    "说明": "教师即将到龄退休，请及时办理退休手续",
    "参数": {
        "教师ID": None,
        "教师姓名": None,
        "选项": [
            {
                "label": "modify_status",
                "名称": "修改任职状态",
                "说明": "请在教师基础信息表中修改当前教师的任职状态",
                "目标表": "teacher_basic_info",
                "操作": "修改任职状态"
            },
            {
                "label": "delayed_retirement",
                "名称": "已批准延迟退休",
                "说明": "该教师已批准延迟退休，请核实延迟退休记录",
                "目标表": "delayed_retirement_records",
                "操作": "核实/填写延迟退休记录"
            }
        ]
    },
    "完成状态": False,
    "已选选项": None
}

cursor.execute('''
    UPDATE todo_templates
    SET task_flow = %s,
        template_name = '到龄退休提醒清单',
        business_type = 'retirement_reminder'
    WHERE template_code = 'RETIREMENT_REMIND'
''', (json.dumps([correct_task]),))

print("  已更新RETIREMENT_REMIND模板")

conn.commit()

# 4. 验证清理结果
print("\n4. 验证清理后的模板：")
cursor.execute('''
    SELECT id, template_code, template_name, business_type
    FROM todo_templates
    WHERE template_code LIKE '%RETIREMENT%' 
       OR template_name LIKE '%退休%'
       OR business_type LIKE '%retirement%'
    ORDER BY id
''')

rows = cursor.fetchall()
print(f"剩余 {len(rows)} 个模板\n")

for row in rows:
    print(f"ID: {row[0]}, 编号: {row[1]}, 名称: {row[2]}, 业务类型: {row[3]}")

cursor.close()
conn.close()

print("\n" + "=" * 70)
print("清理完成")
print("=" * 70)
