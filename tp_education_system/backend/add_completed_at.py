import psycopg2

conn = psycopg2.connect(host='localhost', port='5432', database='taiping_education', user='taiping_user', password='taiping_password')
cur = conn.cursor()

# 检查completed_at字段是否存在
cur.execute("""
    SELECT column_name FROM information_schema.columns 
    WHERE table_name = 'todo_items' AND column_name = 'completed_at'
""")
if not cur.fetchone():
    cur.execute("""
        ALTER TABLE todo_items 
        ADD COLUMN completed_at TIMESTAMP
    """)
    print('已添加 completed_at 字段')
else:
    print('completed_at 字段已存在')

conn.commit()
conn.close()
