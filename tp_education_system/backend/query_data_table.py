from sqlalchemy import create_engine, text

DATABASE_URL = 'postgresql://taiping_user:taiping_password@localhost:5432/taiping_education'
engine = create_engine(DATABASE_URL)

print("=" * 100)
print("查询data表（学校信息表）的结构")
print("=" * 100)

with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'data'
        ORDER BY ordinal_position
    """))
    
    print("\ndata表的字段:")
    for i, row in enumerate(result, 1):
        print(f"  {i}. {row.column_name} ({row.data_type})")

print("\n" + "=" * 100)
print("查询data表的前5行数据")
print("=" * 100)

with engine.connect() as conn:
    result = conn.execute(text("SELECT * FROM data LIMIT 5"))
    
    for row in result:
        print(f"  {row}")

print("=" * 100)
