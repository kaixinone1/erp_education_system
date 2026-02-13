#!/usr/bin/env python3
from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://taiping_user:taiping_password@localhost:5432/taiping_education"
engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'teacher_basic_info' AND table_schema = 'public'
        ORDER BY ordinal_position
    """))
    print("数据库中的字段:")
    for row in result:
        print(f"  {row[0]}: {row[1]}")
