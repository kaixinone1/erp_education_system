#!/usr/bin/env python3
from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://taiping_user:taiping_password@localhost:5432/taiping_education"
engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    # 清空表数据
    conn.execute(text("TRUNCATE TABLE teacher_basic_info RESTART IDENTITY CASCADE"))
    conn.commit()
    print("表已清空，自增ID已重置")
    
    # 验证
    result = conn.execute(text("SELECT COUNT(*) FROM teacher_basic_info"))
    count = result.fetchone()[0]
    print(f"当前数据条数: {count}")
