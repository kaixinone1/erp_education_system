#!/usr/bin/env python3
from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://taiping_user:taiping_password@localhost:5432/taiping_education"
engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    # 获取所有表
    result = conn.execute(text("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
    """))
    tables = [row[0] for row in result]
    
    print(f"发现 {len(tables)} 个表: {tables}")
    
    # 删除所有表
    for table in tables:
        try:
            conn.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE"))
            print(f"已删除表: {table}")
        except Exception as e:
            print(f"删除表 {table} 失败: {e}")
    
    conn.commit()
    print("\n所有表已删除")
