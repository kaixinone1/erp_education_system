#!/usr/bin/env python3
from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://taiping_user:taiping_password@localhost:5432/taiping_education"
engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    # 检查表是否存在
    result = conn.execute(text("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_name = 'teacher_basic_info'
    """))
    tables = [row[0] for row in result]
    print(f'表是否存在: {len(tables) > 0}')
    
    if tables:
        # 检查数据条数
        result = conn.execute(text("SELECT COUNT(*) FROM teacher_basic_info"))
        count = result.fetchone()[0]
        print(f'数据条数: {count}')
        
        # 检查前几行数据
        result = conn.execute(text("SELECT * FROM teacher_basic_info LIMIT 3"))
        rows = result.fetchall()
        print(f'前3行数据:')
        for row in rows:
            print(f'  {row}')
