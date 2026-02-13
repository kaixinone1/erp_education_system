#!/usr/bin/env python3
from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://taiping_user:taiping_password@localhost:5432/taiping_education"
engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    # 检查id列的定义
    result = conn.execute(text("""
        SELECT column_name, data_type, column_default, is_nullable
        FROM information_schema.columns
        WHERE table_name = 'teacher_basic_info' AND column_name = 'id'
    """))
    row = result.fetchone()
    print(f'id列定义: {row}')
    
    # 检查所有ID值
    result = conn.execute(text("SELECT id FROM teacher_basic_info ORDER BY id LIMIT 10"))
    ids = [r[0] for r in result]
    print(f'前10个ID: {ids}')
