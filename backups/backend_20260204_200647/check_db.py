from sqlalchemy import create_engine, text

engine = create_engine('postgresql://taiping_user:taiping_password@localhost:5432/taiping_education')

with engine.connect() as conn:
    # 获取所有表名
    result = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='public'"))
    tables = [row[0] for row in result]
    print('Tables:', tables)
    
    # 检查每个表的数据
    for table in tables:
        try:
            count = conn.execute(text(f'SELECT COUNT(*) FROM {table}')).scalar()
            print(f'{table}: {count} rows')
            if count > 0:
                sample = conn.execute(text(f'SELECT * FROM {table} LIMIT 3')).fetchall()
                for row in sample:
                    print(f'  {row}')
        except Exception as e:
            print(f'{table}: Error - {e}')
