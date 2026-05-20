from sqlalchemy import create_engine, text

DATABASE_URL = 'postgresql://taiping_user:taiping_password@localhost:5432/taiping_education'
engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    # 检查所有字典表
    result = conn.execute(text("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name LIKE '%dict%'
        ORDER BY table_name
    """))
    
    print("数据库中的字典相关表：")
    print("-" * 50)
    dict_tables = []
    for row in result:
        dict_tables.append(row.table_name)
        print(f"  {row.table_name}")
    
    # 检查每个字典表的内容
    for table_name in dict_tables:
        print(f"\n\n{'='*80}")
        print(f"表名：{table_name}")
        print('='*80)
        
        try:
            # 获取表结构
            result = conn.execute(text(f"""
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_name = '{table_name}'
                ORDER BY ordinal_position
            """))
            
            columns = [row.column_name for row in result]
            print(f"字段：{', '.join(columns)}")
            
            # 获取数据
            result = conn.execute(text(f"SELECT * FROM {table_name} LIMIT 10"))
            
            print(f"\n前10条数据：")
            for row in result:
                print(f"  {dict(row._mapping)}")
                
        except Exception as e:
            print(f"  错误：{e}")
