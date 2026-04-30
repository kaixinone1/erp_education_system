import psycopg2
conn = psycopg2.connect(host='localhost', port='5432', database='taiping_education', user='taiping_user', password='taiping_password')
cur = conn.cursor()

# 添加退休到龄提醒
cur.execute('''
    INSERT INTO business_checklist ("清单名称", "触发条件", "是否有效", "关联模板ID", created_at, updated_at)
    VALUES ('退休到龄提醒', '["自动扫描"]', true, 4, NOW(), NOW())
    ON CONFLICT DO NOTHING
''')

# 添加80周岁高龄补贴提醒
cur.execute('''
    INSERT INTO business_checklist ("清单名称", "触发条件", "是否有效", "关联模板ID", created_at, updated_at)
    VALUES ('80周岁高龄补贴提醒', '["自动扫描"]', true, 3, NOW(), NOW())
    ON CONFLICT DO NOTHING
''')

# 添加教师死亡后待办工作
cur.execute('''
    INSERT INTO business_checklist ("清单名称", "触发条件", "是否有效", "关联模板ID", created_at, updated_at)
    VALUES ('教师死亡后待办工作', '["自动扫描"]', true, 2, NOW(), NOW())
    ON CONFLICT DO NOTHING
''')

conn.commit()

# 验证
cur.execute('SELECT id, "清单名称", "关联模板ID" FROM business_checklist')
print('=== business_checklist ===')
for row in cur.fetchall():
    print(f'ID:{row[0]} 名称:{row[1]} 关联模板:{row[2]}')

conn.close()
