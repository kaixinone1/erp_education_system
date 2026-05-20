from sqlalchemy import create_engine, text

engine = create_engine('postgresql://taiping_user:taiping_password@localhost:5432/taiping_education')
conn = engine.connect()

# 查找所有包含teacher的表
result = conn.execute(text("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public' 
    AND (table_name LIKE '%teacher%' OR table_name LIKE '%unit%' OR table_name LIKE '%单位%')
    ORDER BY table_name
"""))
tables = [row[0] for row in result.fetchall()]

print("教师相关表：")
for table in tables:
    print(f"  {table}")

# 检查每个表的结构
for table in tables:
    result = conn.execute(text(f"""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = '{table}' 
        ORDER BY ordinal_position
    """))
    columns = result.fetchall()
    
    print(f"\n{table} 表结构：")
    for col in columns:
        print(f"  {col[0]}: {col[1]}")

conn.close()
