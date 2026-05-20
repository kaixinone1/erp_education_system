from sqlalchemy import create_engine, text

DATABASE_URL = 'postgresql://taiping_user:taiping_password@localhost:5432/taiping_education'
engine = create_engine(DATABASE_URL)

print("=" * 100)
print("查询数据库中的所有表")
print("=" * 100)

with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_type = 'BASE TABLE'
        ORDER BY table_name
    """))
    
    print("\n数据库中的表:")
    for i, row in enumerate(result, 1):
        print(f"  {i}. {row.table_name}")

print("=" * 100)
