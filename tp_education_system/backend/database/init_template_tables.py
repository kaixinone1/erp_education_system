"""
初始化模板管理数据库表
"""
from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, DateTime, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

DATABASE_URL = "postgresql://taiping_user:taiping_password@localhost:5432/taiping_education"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Template(Base):
    """模板主表"""
    __tablename__ = 'templates'
    
    template_id = Column(Integer, primary_key=True, autoincrement=True)
    template_name = Column(String(200), nullable=False, comment='模板名称')
    original_filename = Column(String(200), comment='原始文件名')
    file_path = Column(String(500), comment='文件路径')
    metadata_path = Column(String(500), comment='元数据路径')
    template_type = Column(String(20), default='Excel', comment='模板类型')
    tags = Column(ARRAY(Text), comment='标签数组')
    description = Column(Text, comment='模板描述')
    file_size = Column(Integer, comment='文件大小(字节)')
    row_count = Column(Integer, comment='行数')
    col_count = Column(Integer, comment='列数')
    cell_count = Column(Integer, comment='单元格数')
    merge_count = Column(Integer, comment='合并单元格数')
    usage_count = Column(Integer, default=0, comment='使用次数')
    last_used_at = Column(DateTime, comment='最后使用时间')
    status = Column(String(20), default='active', comment='状态')
    created_at = Column(DateTime, nullable=False, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    created_by = Column(String(100), comment='创建人')


class TemplateTag(Base):
    """模板标签表"""
    __tablename__ = 'template_tags'
    
    tag_id = Column(Integer, primary_key=True, autoincrement=True)
    tag_name = Column(String(50), unique=True, nullable=False, comment='标签名称')
    tag_color = Column(String(20), comment='标签颜色')
    created_at = Column(DateTime, nullable=False, default=datetime.now, comment='创建时间')


class TemplateUsageLog(Base):
    """模板使用记录表"""
    __tablename__ = 'template_usage_logs'
    
    log_id = Column(Integer, primary_key=True, autoincrement=True)
    template_id = Column(Integer, comment='模板ID')
    action = Column(String(50), comment='操作类型')
    user_id = Column(String(100), comment='用户ID')
    details = Column(Text, comment='操作详情')
    created_at = Column(DateTime, nullable=False, default=datetime.now, comment='创建时间')


def init_tables():
    """初始化所有表"""
    Base.metadata.create_all(bind=engine)
    print("模板管理表创建成功")
    
    session = SessionLocal()
    try:
        default_tags = [
            {'tag_name': '退休', 'tag_color': '#409EFF'},
            {'tag_name': '工资', 'tag_color': '#67C23A'},
            {'tag_name': '绩效', 'tag_color': '#E6A23C'},
            {'tag_name': '人事', 'tag_color': '#F56C6C'},
            {'tag_name': '财务', 'tag_color': '#909399'}
        ]
        
        for tag_data in default_tags:
            existing = session.query(TemplateTag).filter_by(tag_name=tag_data['tag_name']).first()
            if not existing:
                tag = TemplateTag(**tag_data)
                session.add(tag)
        
        session.commit()
        print("默认标签创建成功")
        
        all_tags = session.query(TemplateTag).all()
        print(f"\n当前标签列表：")
        for tag in all_tags:
            print(f"  - {tag.tag_name} ({tag.tag_color})")
            
    except Exception as e:
        session.rollback()
        print(f"创建默认标签失败: {e}")
    finally:
        session.close()


if __name__ == '__main__':
    init_tables()
