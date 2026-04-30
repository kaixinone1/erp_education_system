"""
查找用户定义的高龄业务清单
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

# 查看所有表，找可能包含高龄清单的表
cursor.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public'
    AND table_type = 'BASE TABLE'
    ORDER BY table_name
""")
all_tables = cursor.fetchall()

print('=== 所有表名（可能与清单相关）===')
for t in all_tables:
    table_name = t[0]
    if 'checklist' in table_name.lower() or '清单' in table_name or 'todo' in table_name.lower() or '待办' in table_name or '业务' in table_name:
        print(f'  - {table_name}')

# 查看checklist_templates表（旧版模板表）
print('\n=== checklist_templates 表 ===')
try:
    cursor.execute("""
        SELECT id, 模板名称, 模板描述, 适用对象, 状态
        FROM checklist_templates
    """)
    rows = cursor.fetchall()
    for row in rows:
        print(f'  ID: {row[0]}, 名称: {row[1]}, 适用: {row[3]}, 状态: {row[4]}')
except Exception as e:
    print(f'  表不存在或错误: {e}')

# 查看checklist_template_items表
print('\n=== checklist_template_items 表 ===')
try:
    cursor.execute("""
        SELECT i.id, i.模板ID, t.模板名称, i.任务序号, i.任务名称
        FROM checklist_template_items i
        JOIN checklist_templates t ON i.模板ID = t.id
        ORDER BY i.模板ID, i.任务序号
    """)
    rows = cursor.fetchall()
    for row in rows:
        print(f'  模板{row[1]} - {row[3]}. {row[4]}')
except Exception as e:
    print(f'  表不存在或错误: {e}')

# 查找所有可能包含任务项配置的表
print('\n=== 查找包含JSONB任务配置的表 ===')
for t in all_tables:
    table_name = t[0]
    try:
        cursor.execute(f"""
            SELECT column_name 
            FROM information_schema.columns
            WHERE table_name = %s AND data_type = 'jsonb'
        """, (table_name,))
        jsonb_cols = cursor.fetchall()
        if jsonb_cols:
            for col in jsonb_cols:
                print(f'  {table_name}.{col[0]}')
    except:
        pass

cursor.close()
conn.close()
print('\n检查完成!')
