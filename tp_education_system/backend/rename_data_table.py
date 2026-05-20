from sqlalchemy import create_engine, text

DATABASE_URL = 'postgresql://taiping_user:taiping_password@localhost:5432/taiping_education'
engine = create_engine(DATABASE_URL)

print("=" * 100)
print("将data表重命名为school_information_table")
print("=" * 100)

with engine.connect() as conn:
    # 检查data表是否存在
    result = conn.execute(text("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'data'
        )
    """))
    
    if result.fetchone()[0]:
        # 检查school_information_table表是否已存在
        result2 = conn.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'school_information_table'
            )
        """))
        
        if result2.fetchone()[0]:
            print("\nschool_information_table表已存在，删除data表")
            conn.execute(text("DROP TABLE data"))
        else:
            # 重命名表
            conn.execute(text("ALTER TABLE data RENAME TO school_information_table"))
            print("\n[OK] 表重命名成功：data -> school_information_table")
        
        conn.commit()
    else:
        print("\ndata表不存在")

print("=" * 100)
