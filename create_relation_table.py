import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port='5432',
    database='taiping_education',
    user='taiping_user',
    password='taiping_password'
)
cursor = conn.cursor()

# 创建 employee_tag_relations 关系表
cursor.execute("""
    CREATE TABLE IF NOT EXISTS employee_tag_relations (
        id SERIAL PRIMARY KEY,
        employee_id INTEGER NOT NULL,
        tag_id INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(employee_id, tag_id)
    )
""")

conn.commit()

print('employee_tag_relations 表创建成功！')

# 验证
cursor.execute("SELECT COUNT(*) FROM employee_tag_relations")
count = cursor.fetchone()[0]
print(f'当前记录数: {count}')

cursor.close()
conn.close()
