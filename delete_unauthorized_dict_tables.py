from sqlalchemy import create_engine, text

DATABASE_URL = 'postgresql://taiping_user:taiping_password@localhost:5432/taiping_education'
engine = create_engine(DATABASE_URL)

# 需要删除的私自创建的字典表
tables_to_delete = [
    'dict_dictionary_personal',
    'dict_grade_dictionary',
    'dict_title_dictionary'
]

with engine.connect() as conn:
    for table_name in tables_to_delete:
        # 检查表是否存在
        result = conn.execute(text(f"""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = '{table_name}'
            )
        """))
        
        exists = result.fetchone()[0]
        
        if exists:
            # 删除表
            conn.execute(text(f"DROP TABLE IF EXISTS {table_name} CASCADE"))
            print(f"[已删除] {table_name}")
        else:
            print(f"[不存在] {table_name}")
    
    conn.commit()

print("\n清理完成！")
