import psycopg2
import os

conn = psycopg2.connect(
    host='localhost',
    port='5432',
    database='taiping_education',
    user='taiping_user',
    password='taiping_password'
)
cursor = conn.cursor()

# 创建通用模板表
cursor.execute("""
    CREATE TABLE IF NOT EXISTS universal_templates (
        id SERIAL PRIMARY KEY,
        template_id VARCHAR(200) UNIQUE NOT NULL,
        template_name VARCHAR(200) NOT NULL,
        file_path VARCHAR(500) NOT NULL,
        file_type VARCHAR(20) NOT NULL,
        placeholders TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

# 创建字段映射表
cursor.execute("""
    CREATE TABLE IF NOT EXISTS universal_field_mapping (
        id SERIAL PRIMARY KEY,
        placeholder_name VARCHAR(200) NOT NULL,
        table_name VARCHAR(200) NOT NULL,
        field_name VARCHAR(200) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

conn.commit()

# 查看表是否创建成功
cursor.execute("""
    SELECT table_name FROM information_schema.tables 
    WHERE table_schema = 'public' AND table_name IN ('universal_templates', 'universal_field_mapping')
""")
tables = cursor.fetchall()
print("创建的表：")
for t in tables:
    print(f"  - {t[0]}")

cursor.close()
conn.close()
print("\n完成！")
