"""
初始化模板自动填充规则表
"""
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

DATABASE_URL = "postgresql://taiping_user:taiping_password@localhost:5432/taiping_education"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class TemplateAutoFillRule(Base):
    """模板自动填充规则表"""
    __tablename__ = 'template_auto_fill_rules'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    label_pattern = Column(String(100), nullable=False, comment='标签文本模式')
    fill_type = Column(String(50), nullable=False, default='current_date', comment='填充类型')
    date_format = Column(String(50), nullable=False, default='YYYY年MM月DD日', comment='日期格式')
    position = Column(String(50), nullable=False, default='same_row_next_cell', comment='填充位置')
    enabled = Column(Boolean, nullable=False, default=True, comment='是否启用')
    description = Column(Text, comment='规则描述')
    created_at = Column(DateTime, nullable=False, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, comment='更新时间')


def init_table():
    """初始化表并插入默认规则"""
    Base.metadata.create_all(bind=engine)
    
    session = SessionLocal()
    try:
        existing = session.query(TemplateAutoFillRule).filter_by(
            label_pattern='**日期：'
        ).first()
        
        if not existing:
            default_rule = TemplateAutoFillRule(
                label_pattern='**日期：',
                fill_type='current_date',
                date_format='YYYY年MM月DD日',
                position='same_row_next_cell',
                enabled=True,
                description='自动填充当前日期到**日期：后的空白单元格'
            )
            session.add(default_rule)
            session.commit()
            print("默认规则已创建：**日期： -> 自动填充当前日期")
        else:
            print("默认规则已存在，跳过创建")
    except Exception as e:
        session.rollback()
        print(f"初始化失败: {e}")
    finally:
        session.close()


if __name__ == '__main__':
    init_table()
