import json
import psycopg2

# 数据库连接
conn = psycopg2.connect(
    host='localhost',
    port='5432',
    database='taiping_education',
    user='taiping_user',
    password='taiping_password'
)
cursor = conn.cursor()

# 读取配置文件
config_file = 'd:/erp_thirteen/tp_education_system/backend/config/merged_schema_mappings.json'
with open(config_file, 'r', encoding='utf-8') as f:
    config = json.load(f)

tables_config = config.get('tables', {})

# 获取所有表
cursor.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
    ORDER BY table_name
""")

tables = [row[0] for row in cursor.fetchall()]

print('需要配置字段中文名的表：\n')

for table_name in tables:
    # 获取表字段
    cursor.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = %s AND table_schema = 'public'
        ORDER BY ordinal_position
    """, (table_name,))
    
    columns = [row[0] for row in cursor.fetchall()]
    
    # 检查配置
    table_config = tables_config.get(table_name, {})
    fields_config = table_config.get('fields', [])
    
    if isinstance(fields_config, list) and len(fields_config) > 0:
        # 已有字段配置
        continue
    
    print(f'{table_name}:')
    print(f'  字段: {columns}')
    print()

cursor.close()
conn.close()
