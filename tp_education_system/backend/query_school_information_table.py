from sqlalchemy import create_engine, text

DATABASE_URL = 'postgresql://taiping_user:taiping_password@localhost:5432/taiping_education'
engine = create_engine(DATABASE_URL)

print("=" * 100)
print("查询school_information_table表")
print("=" * 100)

with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_type = 'BASE TABLE'
        AND table_name = 'school_information_table'
    """))
    
    tables = list(result)
    
    if tables:
        print("\n找到school_information_table表！")
        
        # 查询表结构
        result2 = conn.execute(text("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'school_information_table'
            ORDER BY ordinal_position
        """))
        
        print("\nschool_information_table表的字段:")
        for i, row in enumerate(result2, 1):
            print(f"  {i}. {row.column_name} ({row.data_type})")
        
        # 查询前5行数据
        print("\nschool_information_table表的前5行数据:")
        result3 = conn.execute(text("SELECT * FROM school_information_table LIMIT 5"))
        
        for row in result3:
            print(f"  {row}")
    else:
        print("\n没有找到school_information_table表")

print("=" * 100)
