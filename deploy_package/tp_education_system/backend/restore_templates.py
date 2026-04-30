import psycopg2
import json

conn = psycopg2.connect(host='localhost', port='5432', database='taiping_education', user='taiping_user', password='taiping_password')
cur = conn.cursor()

# 恢复死亡模板
cur.execute("""
    INSERT INTO todo_templates (template_code, template_name, business_type, description, is_enabled, created_at, updated_at)
    VALUES ('DEATH_001', '教师死亡后待办工作', 'DEATH', '教师死亡后待办工作清单', true, NOW(), NOW())
    ON CONFLICT (template_code) DO NOTHING
""")

conn.commit()
print('已恢复DEATH_001模板')

# 查看当前模板
cur.execute('SELECT template_code, template_name FROM todo_templates')
print('\n当前模板:')
for row in cur.fetchall():
    print(f'  {row[0]}: {row[1]}')

conn.close()
