import psycopg2

DATABASE_CONFIG = {
    'host': 'localhost',
    'port': '5432',
    'database': 'taiping_education',
    'user': 'taiping_user',
    'password': 'taiping_password'
}

conn = psycopg2.connect(**DATABASE_CONFIG)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS delayed_retirement_records (
    id SERIAL PRIMARY KEY,
    "教师id" INTEGER,
    "批准日期" DATE,
    "退休年龄" INTEGER DEFAULT 60,
    "备注" TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()
print('延迟退休记录表创建成功')

cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'delayed_retirement_records'")
if cursor.fetchone():
    print('表已存在')
else:
    print('表创建失败')

cursor.close()
conn.close()
