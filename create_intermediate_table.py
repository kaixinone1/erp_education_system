"""
创建中间表定义存储表
"""
import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port='5432',
    database='taiping_education',
    user='taiping_user',
    password='taiping_password'
)
cursor = conn.cursor()

# 创建中间表定义表
cursor.execute("""
    CREATE TABLE IF NOT EXISTS intermediate_tables (
        id SERIAL PRIMARY KEY,
        table_name VARCHAR(255) NOT NULL UNIQUE,
        table_name_cn VARCHAR(255) NOT NULL,
        description TEXT,
        fields JSONB DEFAULT '[]',
        is_active BOOLEAN DEFAULT true,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

# 检查是否已有中间表数据
cursor.execute("SELECT COUNT(*) FROM intermediate_tables")
count = cursor.fetchone()[0]

if count == 0:
    # 插入一个示例中间表（退休呈报数据）
    cursor.execute("""
        INSERT INTO intermediate_tables (table_name, table_name_cn, description, fields)
        VALUES (
            'retirement_report_data',
            '退休呈报数据',
            '用于存储退休呈报相关数据',
            '[{"name": "teacher_id", "label": "教师ID", "type": "integer"}, {"name": "姓名", "label": "姓名", "type": "varchar"}, {"name": "性别", "label": "性别", "type": "varchar"}]'
        )
    """)

conn.commit()
print("中间表定义表创建成功！")

cursor.close()
conn.close()
