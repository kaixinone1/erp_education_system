import psycopg2

conn = psycopg2.connect(
    host='localhost', 
    port='5432', 
    database='taiping_education', 
    user='taiping_user', 
    password='taiping_password'
)
cur = conn.cursor()

# 检查表是否存在
cur.execute("""
    SELECT EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name = 'retirement_cert_records'
    )
""")
table_exists = cur.fetchone()[0]

if not table_exists:
    # 创建表
    cur.execute("""
        CREATE TABLE retirement_cert_records (
            id SERIAL PRIMARY KEY,
            教师ID INTEGER,
            教师姓名 VARCHAR(100),
            签发日期 DATE,
            退休证编号 VARCHAR(50),
            签收人 VARCHAR(100),
            签收日期 DATE,
            备注 TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("表 retirement_cert_records 创建成功")
else:
    # 检查并添加缺失的字段
    cur.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'retirement_cert_records'
    """)
    existing_columns = [row[0] for row in cur.fetchall()]
    
    columns_to_add = {
        '签发日期': 'DATE',
        '退休证编号': 'VARCHAR(50)',
        '备注': 'TEXT'
    }
    
    for col_name, col_type in columns_to_add.items():
        if col_name not in existing_columns:
            cur.execute(f"ALTER TABLE retirement_cert_records ADD COLUMN {col_name} {col_type}")
            print(f"添加字段: {col_name}")
    
    print("表结构检查完成")

conn.commit()
cur.close()
conn.close()
print("完成")
