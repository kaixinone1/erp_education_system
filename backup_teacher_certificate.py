from sqlalchemy import create_engine, text

engine = create_engine('postgresql://taiping_user:taiping_password@localhost:5432/taiping_education')
conn = engine.connect()

# 备份teacher_certificate_info表
try:
    # 检查备份表是否已存在
    result = conn.execute(text("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'teacher_certificate_info_backup'
        )
    """))
    backup_exists = result.fetchone()[0]
    
    if backup_exists:
        print("备份表已存在，先删除旧备份...")
        conn.execute(text("DROP TABLE teacher_certificate_info_backup"))
    
    # 创建备份
    conn.execute(text("CREATE TABLE teacher_certificate_info_backup AS SELECT * FROM teacher_certificate_info"))
    conn.commit()
    
    # 验证备份
    result = conn.execute(text("SELECT COUNT(*) FROM teacher_certificate_info_backup"))
    backup_count = result.fetchone()[0]
    
    result = conn.execute(text("SELECT COUNT(*) FROM teacher_certificate_info"))
    original_count = result.fetchone()[0]
    
    print(f"备份完成！")
    print(f"  原表记录数：{original_count}")
    print(f"  备份表记录数：{backup_count}")
    
    if backup_count == original_count:
        print("  ✓ 备份成功，记录数一致")
    else:
        print("  ✗ 备份失败，记录数不一致")
        
except Exception as e:
    print(f"备份失败：{e}")
    conn.rollback()
finally:
    conn.close()
