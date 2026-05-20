from sqlalchemy import create_engine, text

DATABASE_URL = 'postgresql://taiping_user:taiping_password@localhost:5432/taiping_education'
engine = create_engine(DATABASE_URL)

print("=" * 100)
print("查询所有表（查找学校信息表）")
print("=" * 100)

with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_type = 'BASE TABLE'
        ORDER BY table_name
    """))
    
    print("\n数据库中的所有表:")
    for i, row in enumerate(result, 1):
        print(f"  {i}. {row.table_name}")

print("\n" + "=" * 100)
print("查找包含'学校'、'school'、'单位'、'unit'的表")
print("=" * 100)

with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_type = 'BASE TABLE'
        AND (
            table_name ILIKE '%学校%' 
            OR table_name ILIKE '%school%'
            OR table_name ILIKE '%单位%'
            OR table_name ILIKE '%unit%'
        )
        ORDER BY table_name
    """))
    
    tables = list(result)
    
    if tables:
        print("\n找到相关的表:")
        for i, row in enumerate(tables, 1):
            print(f"  {i}. {row.table_name}")
    else:
        print("\n没有找到相关表，列出所有表供参考")

print("=" * 100)
