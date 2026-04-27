import psycopg2

conn = psycopg2.connect(host='localhost', port='5432', database='taiping_education', user='taiping_user', password='taiping_password')
cur = conn.cursor()

# 创建待办历史记录表
cur.execute("""
    CREATE TABLE IF NOT EXISTS todo_history (
        id SERIAL PRIMARY KEY,
        todo_id INTEGER NOT NULL,
        teacher_id INTEGER NOT NULL,
        teacher_name VARCHAR(100),
        template_code VARCHAR(100),
        business_type VARCHAR(50),
        title VARCHAR(500),
        description TEXT,
        status VARCHAR(20) NOT NULL DEFAULT 'completed',
        completed_at TIMESTAMP,
        created_at TIMESTAMP NOT NULL,
        task_items JSONB,
        return_count INTEGER DEFAULT 0,
        return_reason TEXT,
        archived_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")
print('已创建 todo_history 表')

conn.commit()
conn.close()
