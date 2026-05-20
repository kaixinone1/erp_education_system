from sqlalchemy import create_engine, text

DATABASE_URL = 'postgresql://taiping_user:taiping_password@localhost:5432/taiping_education'
engine = create_engine(DATABASE_URL)

print("=" * 100)
print("查询 teacher_unit 表的列")
print("=" * 100)

with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'teacher_unit'
        ORDER BY ordinal_position
    """))
    
    print("\nteacher_unit 表的列:")
    for i, row in enumerate(result, 1):
        print(f"  {i}. {row.column_name} ({row.data_type})")

print("=" * 100)

print("\n查询 teacher_unit 表的前5行数据:")
print("=" * 100)

with engine.connect() as conn:
    result = conn.execute(text("SELECT * FROM teacher_unit LIMIT 5"))
    
    for row in result:
        print(row)

print("=" * 100)
