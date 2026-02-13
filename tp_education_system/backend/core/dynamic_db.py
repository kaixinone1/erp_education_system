from sqlalchemy import create_engine, Column, Table, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Dict, Any, Optional, List
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 数据库连接信息
DATABASE_URL = "postgresql://taiping_user:taiping_password@localhost:5432/taiping_education"

# 创建数据库引擎
engine = create_engine(DATABASE_URL)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建Base类
Base = declarative_base()

# 创建元数据对象
metadata = MetaData()

class DynamicTableManager:
    """动态表管理器
    
    负责根据表结构定义动态创建或更新数据库表
    """
    
    def __init__(self):
        """初始化动态表管理器"""
        self.engine = engine
        self.metadata = metadata
        self.session_factory = SessionLocal
    
    def get_session(self) -> Session:
        """获取数据库会话
        
        Returns:
            数据库会话对象
        """
        return self.session_factory()
    
    def create_or_update_table_from_schema(self, table_name: str, schema_definition: Dict[str, Any]) -> bool:
        """根据表结构定义创建或更新表
        
        Args:
            table_name: 表名
            schema_definition: 表结构定义
        
        Returns:
            是否成功
        """
        try:
            logger.info(f"Processing table: {table_name}")
            
            # 解析字段定义
            columns = []
            
            for field_name, field_def in schema_definition.get('fields', {}).items():
                # 映射字段类型
                column_type = self._map_field_type(field_def.get('type'))
                if not column_type:
                    logger.warning(f"Unknown field type for {field_name}: {field_def.get('type')}")
                    continue
                
                # 创建列
                column_args = {
                    'nullable': not field_def.get('required', False)
                }
                
                # 添加默认值
                if 'default' in field_def:
                    column_args['default'] = field_def['default']
                
                # 添加主键
                if field_def.get('primary_key', False):
                    column_args['primary_key'] = True
                
                column = Column(field_name, column_type, **column_args)
                columns.append(column)
            
            if not columns:
                logger.error(f"No valid columns found for table {table_name}")
                return False
            
            # 创建或更新表
            table = Table(table_name, self.metadata, *columns, extend_existing=True)
            
            # 执行DDL
            table.create(bind=self.engine, checkfirst=True)
            
            logger.info(f"Table {table_name} processed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error processing table {table_name}: {e}")
            return False
    
    def _map_field_type(self, field_type: str) -> Any:
        """映射字段类型
        
        Args:
            field_type: 字段类型字符串
        
        Returns:
            SQLAlchemy字段类型
        """
        from sqlalchemy import String, Integer, Float, Boolean, Date, DateTime, Text
        
        type_mapping = {
            'string': String,
            'integer': Integer,
            'float': Float,
            'boolean': Boolean,
            'date': Date,
            'datetime': DateTime,
            'text': Text
        }
        
        # 处理带长度的类型，如 string(50)
        if '(' in field_type and ')' in field_type:
            base_type, length = field_type.split('(')
            length = length.rstrip(')')
            if base_type in type_mapping:
                if base_type == 'string':
                    return String(int(length))
        
        return type_mapping.get(field_type, String)
    
    def drop_table(self, table_name: str) -> bool:
        """删除表
        
        Args:
            table_name: 表名
        
        Returns:
            是否成功
        """
        try:
            table = Table(table_name, self.metadata, autoload_with=self.engine)
            table.drop(bind=self.engine)
            logger.info(f"Table {table_name} dropped successfully")
            return True
        except Exception as e:
            logger.error(f"Error dropping table {table_name}: {e}")
            return False
    
    def get_table_exists(self, table_name: str) -> bool:
        """检查表是否存在
        
        Args:
            table_name: 表名
        
        Returns:
            是否存在
        """
        from sqlalchemy import inspect
        
        inspector = inspect(self.engine)
        return table_name in inspector.get_table_names()
    
    # 基础CRUD封装
    def insert(self, table_name: str, data: Dict[str, Any]) -> bool:
        """插入数据
        
        Args:
            table_name: 表名
            data: 要插入的数据
        
        Returns:
            是否成功
        """
        try:
            with self.get_session() as session:
                # 动态获取表
                table = Table(table_name, self.metadata, autoload_with=self.engine)
                
                # 插入数据
                session.execute(table.insert().values(**data))
                session.commit()
                return True
        except Exception as e:
            logger.error(f"Error inserting data into {table_name}: {e}")
            return False
    
    def update(self, table_name: str, conditions: Dict[str, Any], data: Dict[str, Any]) -> bool:
        """更新数据
        
        Args:
            table_name: 表名
            conditions: 更新条件
            data: 要更新的数据
        
        Returns:
            是否成功
        """
        try:
            with self.get_session() as session:
                table = Table(table_name, self.metadata, autoload_with=self.engine)
                
                # 构建条件
                where_clause = []
                for key, value in conditions.items():
                    where_clause.append(table.c[key] == value)
                
                # 执行更新
                session.execute(table.update().where(*where_clause).values(**data))
                session.commit()
                return True
        except Exception as e:
            logger.error(f"Error updating data in {table_name}: {e}")
            return False
    
    def delete(self, table_name: str, conditions: Dict[str, Any]) -> bool:
        """删除数据
        
        Args:
            table_name: 表名
            conditions: 删除条件
        
        Returns:
            是否成功
        """
        try:
            with self.get_session() as session:
                table = Table(table_name, self.metadata, autoload_with=self.engine)
                
                # 构建条件
                where_clause = []
                for key, value in conditions.items():
                    where_clause.append(table.c[key] == value)
                
                # 执行删除
                session.execute(table.delete().where(*where_clause))
                session.commit()
                return True
        except Exception as e:
            logger.error(f"Error deleting data from {table_name}: {e}")
            return False
    
    def select(self, table_name: str, conditions: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """查询数据
        
        Args:
            table_name: 表名
            conditions: 查询条件
        
        Returns:
            查询结果列表
        """
        try:
            with self.get_session() as session:
                table = Table(table_name, self.metadata, autoload_with=self.engine)
                
                # 构建查询
                query = table.select()
                
                # 添加条件
                if conditions:
                    where_clause = []
                    for key, value in conditions.items():
                        where_clause.append(table.c[key] == value)
                    query = query.where(*where_clause)
                
                # 执行查询
                result = session.execute(query)
                
                # 转换结果
                rows = []
                for row in result:
                    rows.append(dict(row._mapping))
                
                return rows
        except Exception as e:
            logger.error(f"Error selecting data from {table_name}: {e}")
            return []

# 创建全局实例
dynamic_table_manager = DynamicTableManager()
