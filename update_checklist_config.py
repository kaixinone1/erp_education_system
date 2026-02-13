#!/usr/bin/env python3
"""更新清单模板配置，使用template_name替代template_id"""
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
    
    print(f"\n更新清单: {checklist_name} (ID: {checklist_id})")
    
    updated = False
    for task in tasks:
        params = task.get('参数', {})
        old_template_id = params.get('template_id')
        
        if old_template_id:
            # 将template_id映射为template_name
            # 规则：根据template_id查找对应的文件名
            cursor.execute("""
                SELECT file_name FROM document_templates
                WHERE template_id = %s
            """, (old_template_id,))
            result = cursor.fetchone()
            
            if result:
                template_name = result[0]
                # 更新参数：删除template_id，添加template_name
                del params['template_id']
                params['template_name'] = template_name
                updated = True
                print(f"  任务: {task.get('标题')}")
                print(f"    {old_template_id} -> {template_name}")
            else:
                # 如果找不到，尝试模糊匹配
                # 提取关键词（如"退休呈报"）
                keyword = old_template_id.replace('职工', '').replace('html', '').replace('表', '')
                cursor.execute("""
                    SELECT file_name FROM document_templates
                    WHERE file_name LIKE %s
                    LIMIT 1
                """, (f'%{keyword}%',))
                result = cursor.fetchone()
                
                if result:
                    template_name = result[0]
                    del params['template_id']
                    params['template_name'] = template_name
                    updated = True
                    print(f"  任务: {task.get('标题')} (模糊匹配)")
                    print(f"    {old_template_id} -> {template_name}")
                else:
                    print(f"  警告: 找不到模板 {old_template_id}")
    
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
