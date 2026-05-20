from sqlalchemy import create_engine, text

engine = create_engine('postgresql://taiping_user:taiping_password@localhost:5432/taiping_education')
conn = engine.connect()

# 重命名字段
alter_sqls = [
    "ALTER TABLE teacher_certificate_info RENAME COLUMN field_5 TO certificate_type",
    "ALTER TABLE teacher_certificate_info RENAME COLUMN field_6 TO education_stage_subject",
    "ALTER TABLE teacher_certificate_info RENAME COLUMN field_7 TO subject",
    "ALTER TABLE teacher_certificate_info RENAME COLUMN field_8 TO issuing_authority"
]

try:
    for sql in alter_sqls:
        conn.execute(text(sql))
        print(f"执行成功: {sql}")
    
    conn.commit()
    print("\n数据库表结构更新完成！")
    
    # 验证修改
    result = conn.execute(text("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'teacher_certificate_info' 
        ORDER BY ordinal_position
    """))
    columns = [row[0] for row in result.fetchall()]
    print(f"\n当前字段列表: {columns}")
    
except Exception as e:
    print(f"执行失败: {e}")
    conn.rollback()
finally:
    conn.close()
