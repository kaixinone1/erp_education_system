import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port='5432',
    database='taiping_education',
    user='taiping_user',
    password='taiping_password'
)
cursor = conn.cursor()

# 检查当前表结构
cursor.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = 'template_page_settings'
    ORDER BY ordinal_position
""")

print('当前 template_page_settings 表结构:')
for row in cursor.fetchall():
    print(f'  {row[0]}: {row[1]}')

# 添加缺失的字段
missing_columns = [
    ('orientation', 'VARCHAR(20) DEFAULT \'portrait\''),
    ('width_cm', 'NUMERIC(10,2) DEFAULT 21.0'),
    ('height_cm', 'NUMERIC(10,2) DEFAULT 29.7'),
    ('margin_left_cm', 'NUMERIC(10,2) DEFAULT 2.5'),
    ('margin_right_cm', 'NUMERIC(10,2) DEFAULT 2.5'),
    ('margin_top_cm', 'NUMERIC(10,2) DEFAULT 2.5'),
    ('margin_bottom_cm', 'NUMERIC(10,2) DEFAULT 2.5'),
]

for col_name, col_type in missing_columns:
    # 检查字段是否存在
    cursor.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'template_page_settings' AND column_name = %s
    """, (col_name,))
    
    if not cursor.fetchone():
        try:
            cursor.execute(f"ALTER TABLE template_page_settings ADD COLUMN {col_name} {col_type}")
            print(f'添加字段: {col_name}')
        except Exception as e:
            print(f'添加字段 {col_name} 失败: {e}')
    else:
        print(f'字段已存在: {col_name}')

conn.commit()

# 再次检查表结构
cursor.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = 'template_page_settings'
    ORDER BY ordinal_position
""")

print('\n更新后 template_page_settings 表结构:')
for row in cursor.fetchall():
    print(f'  {row[0]}: {row[1]}')

cursor.close()
conn.close()
