"""
更新自动填充规则为模糊匹配
"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://taiping_user:taiping_password@localhost:5432/taiping_education"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

session = SessionLocal()
try:
    session.execute(
        text("""
            UPDATE template_auto_fill_rules 
            SET label_pattern = '日期：',
                description = '自动填充当前日期到包含"日期："标签后的空白单元格（模糊匹配）',
                updated_at = NOW()
            WHERE id = 1
        """)
    )
    session.commit()
    print("规则已更新为模糊匹配：日期：")
    
    result = session.execute(text("SELECT * FROM template_auto_fill_rules WHERE id = 1"))
    row = result.fetchone()
    if row:
        print(f"当前规则：{row.label_pattern}")
        print(f"描述：{row.description}")
except Exception as e:
    session.rollback()
    print(f"更新失败: {e}")
finally:
    session.close()
