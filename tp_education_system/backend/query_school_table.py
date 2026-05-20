from sqlalchemy import create_engine, text

DATABASE_URL = 'postgresql://taiping_user:taiping_password@localhost:5432/taiping_education'
engine = create_engine(DATABASE_URL)

print("=" * 100)
print("查询学校信息表")
print("=" * 100)

with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_type = 'BASE TABLE'
        AND table_name LIKE '%学校%' OR table_name LIKE '%school%'
        ORDER BY table_name
    """))
    
    tables = list(result)
    
    if tables:
        print("\n找到学校相关的表:")
        for i, row in enumerate(tables, 1):
            print(f"  {i}. {row.table_name}")
    else:
        print("\n没有找到学校相关的表")

print("=" * 100)
