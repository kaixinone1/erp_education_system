"""
检查系统中的表和字段
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

# 查询所有业务表
cursor.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public' 
    AND table_type = 'BASE TABLE'
    AND table_name NOT LIKE 'pg_%'
    AND table_name NOT LIKE 'sql_%'
    ORDER BY table_name
""")

tables = [row[0] for row in cursor.fetchall()]
print(f"系统中的表 ({len(tables)}个):")
for t in tables:
    print(f"  - {t}")

# 汇总所有表的字段
print("\n" + "="*50)
print("所有表的字段汇总:")

all_fields = {}
for table in tables:
    cursor.execute(f"""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = '{table}'
        ORDER BY ordinal_position
    """)
    columns = [row[0] for row in cursor.fetchall()]
    all_fields[table] = columns
    
print(f"\n字段汇总 (按表分组):")
for table, cols in all_fields.items():
    print(f"  {table}: {cols}")

# 收集所有唯一字段
unique_fields = set()
for table, cols in all_fields.items():
    for col in cols:
        unique_fields.add(col)

print(f"\n唯一字段数量: {len(unique_fields)}")
print(f"所有唯一字段: {sorted(unique_fields)}")

cursor.close()
conn.close()
