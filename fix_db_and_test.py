#!/usr/bin/env python3
"""修复数据库配置"""
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

# 1. 检查文档模板的实际 template_id
print("=" * 60)
print("1. 文档模板")
print("=" * 60)
cursor.execute("SELECT template_id, file_name FROM document_templates")
for row in cursor.fetchall():
    print(f"  {row[0]} -> {row[1]}")

# 2. 检查清单模板配置
print("\n" + "=" * 60)
print("2. 清单模板配置")
print("=" * 60)
cursor.execute("SELECT 任务项列表 FROM business_checklist WHERE 是否有效 = true")
row = cursor.fetchone()
if row:
    tasks = row[0] or []
    for i, task in enumerate(tasks):
        print(f"\n  任务{i+1}: {task.get('标题')}")
        params = task.get('参数', {})
        for k, v in params.items():
            print(f"    {k}: {v}")
        
        # 添加 template_id 字段（如果不存在）
        if 'template_id' not in params and 'template_name' in params:
            # 通过 template_name 查找对应的 template_id
            template_name = params['template_name']
            cursor.execute(
                "SELECT template_id FROM document_templates WHERE file_name = %s",
                (template_name,)
            )
            result = cursor.fetchone()
            if result:
                params['template_id'] = result[0]
                print(f"    -> 添加 template_id: {result[0]}")
    
    # 更新数据库
    cursor.execute(
        "UPDATE business_checklist SET 任务项列表 = %s WHERE 是否有效 = true",
        (json.dumps(tasks),)
    )
    conn.commit()
    print("\n  ✓ 已更新数据库")

cursor.close()
conn.close()
print("\n完成!")
