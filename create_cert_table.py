import psycopg2

conn = psycopg2.connect(host='localhost', port='5432', database='taiping_education', user='taiping_user', password='taiping_password')
cur = conn.cursor()

# 创建签发退休证中间表
cur.execute("""
    CREATE TABLE IF NOT EXISTS retirement_certificate_data (
        id SERIAL PRIMARY KEY,
        teacher_id INTEGER NOT NULL,
        teacher_name VARCHAR(100),
        id_card VARCHAR(20),
        recipient_name VARCHAR(100),
        receive_date DATE,
        certificate_number VARCHAR(50),
        remarks TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

conn.commit()
print("签发退休证中间表创建成功")

# 检查中间表字段
cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'intermediate_tables'")
cols = [row[0] for row in cur.fetchall()]
print(f"中间表字段: {cols}")

# 注册到中间表（使用正确的字段）
if 'table_display_name' in cols:
    cur.execute("""
        INSERT INTO intermediate_tables (table_name, table_display_name, category, description)
        VALUES ('retirement_certificate_data', '签发退休证数据', '退休管理', '记录退休证签发信息')
        ON CONFLICT (table_name) DO NOTHING
    """)
else:
    cur.execute("""
        INSERT INTO intermediate_tables (table_name, 显示名称, 分类, 描述)
        VALUES ('retirement_certificate_data', '签发退休证数据', '退休管理', '记录退休证签发信息')
        ON CONFLICT (table_name) DO NOTHING
    """)

conn.commit()
cur.close()
conn.close()
print("中间表注册完成")
