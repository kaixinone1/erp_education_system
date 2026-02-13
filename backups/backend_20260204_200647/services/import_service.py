from typing import List, Dict, Any, Optional
import json
import os
from datetime import datetime
from sqlalchemy import create_engine, Table, Column, MetaData, String, Integer, Float, Date, DateTime, Boolean, Text, Numeric, ForeignKey
from sqlalchemy.sql import text


class ImportService:
    """导入服务 - 实现原子化导入操作，支持主表-子表-字典表关系"""
    
    def __init__(self, db_url: str = None):
        # 使用与dynamic_db.py一致的数据库连接
        if db_url is None:
            db_url = "postgresql://taiping_user:taiping_password@localhost:5432/taiping_education"
        self.engine = create_engine(db_url)
        self.metadata = MetaData()
        
        # 配置文件路径
        self.config_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config')
        self.navigation_file = os.path.join(self.config_dir, 'navigation.json')
        self.schema_file = os.path.join(self.config_dir, 'merged_schema_mappings.json')
        self.table_schemas_file = os.path.join(self.config_dir, 'table_schemas.json')
        self.field_mappings_file = os.path.join(self.config_dir, 'field_mappings.json')
    
    def import_data(self, 
                   table_name: str,
                   field_configs: List[Dict[str, Any]],
                   data: List[Dict[str, Any]],
                   module_id: str,
                   module_name: str,
                   table_type: str = "master",
                   parent_table: Optional[str] = None,
                   foreign_keys: Optional[List[Dict[str, Any]]] = None,
                   file_name: str = "",
                   chinese_title: str = "",
                   sub_module_id: str = "",
                   sub_module_name: str = "") -> Dict[str, Any]:
        """
        原子化导入数据，支持表关系处理
        :param table_name: 目标表名
        :param field_configs: 字段配置
        :param data: 要导入的数据
        :param module_id: 归属模块ID
        :param module_name: 归属模块名称
        :param table_type: 表类型 (master/child/dictionary)
        :param parent_table: 父表名（子表使用）
        :param foreign_keys: 外键配置列表
        :param file_name: 原始文件名
        :param chinese_title: 中文标题（从文件名提取）
        :param sub_module_id: 子模块ID
        :param sub_module_name: 子模块名称
        :return: 导入结果
        """
        try:
            # 增强表类型识别：根据文件名和表名判断是否为字典表
            if table_type == "master":
                # 检查文件名中是否包含字典相关关键词
                if file_name:
                    lower_file_name = file_name.lower()
                    if any(keyword in lower_file_name for keyword in ["字典", "类型", "层次", "dict", "type", "level"]):
                        table_type = "dictionary"
                        print(f"根据文件名 '{file_name}' 自动识别为字典表")
                # 检查表名中是否包含字典相关关键词
                elif table_name:
                    lower_table_name = table_name.lower()
                    if any(keyword in lower_table_name for keyword in ["字典", "类型", "层次", "dict", "type", "level"]):
                        table_type = "dictionary"
                        print(f"根据表名 '{table_name}' 自动识别为字典表")
            
            # 步骤1: 动态建表（根据表类型）
            # 返回实际使用的表名和是否是已存在的表
            actual_table_name, is_existing_table = self._create_or_update_table(
                table_name=table_name,
                field_configs=field_configs,
                table_type=table_type,
                parent_table=parent_table,
                foreign_keys=foreign_keys
            )
            
            # 步骤2: 数据清洗与入库（处理外键关联）
            # 如果是已存在的表，使用智能插入/更新逻辑
            if is_existing_table:
                inserted_count, updated_count, errors = self._upsert_data_with_relations(
                    table_name=actual_table_name,
                    field_configs=field_configs,
                    data=data,
                    table_type=table_type,
                    parent_table=parent_table
                )
                total_count = inserted_count + updated_count
                if total_count > 0:
                    message = f"成功导入 {total_count} 条数据（新增 {inserted_count} 条，更新 {updated_count} 条）"
                else:
                    message = "警告: 没有数据被导入，请检查数据格式是否正确"
            else:
                inserted_count, errors = self._insert_data_with_relations(
                    table_name=actual_table_name,
                    field_configs=field_configs,
                    data=data,
                    table_type=table_type,
                    parent_table=parent_table
                )
                total_count = inserted_count
                if total_count > 0:
                    message = f"成功导入 {inserted_count} 条数据"
                else:
                    message = "警告: 没有数据被导入，请检查数据格式是否正确"
            
            # 使用实际表名更新配置
            table_name = actual_table_name
            
            # 步骤3: 更新配置文件
            self._update_schema_config(
                table_name=table_name,
                field_configs=field_configs,
                table_type=table_type,
                parent_table=parent_table,
                foreign_keys=foreign_keys
            )
            
            # 步骤4: 更新导航（根据表类型组织）
            self._update_navigation_config(
                table_name=table_name,
                module_id=module_id,
                module_name=module_name,
                field_configs=field_configs,
                table_type=table_type,
                parent_table=parent_table,
                chinese_title=chinese_title,
                sub_module_id=sub_module_id,
                sub_module_name=sub_module_name
            )
            
            # 步骤5: 更新关系配置
            self._update_relationship_config(
                table_name=table_name,
                table_type=table_type,
                parent_table=parent_table
            )
            
            result = {
                "status": "success",
                "message": message,
                "table_name": table_name,
                "table_type": table_type,
                "record_count": total_count,
                "is_existing_table": is_existing_table
            }
            
            # 如果有错误，添加错误信息
            if errors:
                result["errors"] = errors
                result["status"] = "partial_success"
            
            return result
            
        except Exception as e:
            # 发生错误时回滚
            error_message = f"导入失败: {str(e)}"
            print(f"导入数据时发生错误: {error_message}")
            raise Exception(error_message)
    
    def _create_or_update_table(self, 
                               table_name: str, 
                               field_configs: List[Dict[str, Any]],
                               table_type: str = "master",
                               parent_table: Optional[str] = None,
                               foreign_keys: Optional[List[Dict[str, Any]]] = None) -> tuple:
        """
        动态创建或更新数据表，支持外键约束
        返回: (实际使用的表名, 是否是已存在的表)
        """
        # 首先检查用户指定的表名是否已存在
        if self._table_exists_in_db(table_name):
            # 表已存在，使用现有表
            print(f"表 {table_name} 已存在，将使用现有表导入数据")
            return table_name, True
        
        # 检查是否存在结构相同的表
        existing_table_name = self._find_matching_table(field_configs, table_type)
        
        if existing_table_name:
            # 找到匹配的表，使用现有表
            print(f"找到匹配的表: {existing_table_name}，将使用现有表导入数据")
            return existing_table_name, True
        
        # 没有找到匹配的表，创建新表
        self._create_new_table(table_name, field_configs, table_type, parent_table, foreign_keys)
        return table_name, False
    
    def _find_matching_table(self, field_configs: List[Dict[str, Any]], table_type: str = "master") -> Optional[str]:
        """
        查找是否存在字段结构100%匹配的现有表
        :param field_configs: 字段配置
        :param table_type: 表类型 (master/child/dictionary)
        :return: 匹配的表名或None
        """
        # 直接从数据库获取所有表的结构，而不是依赖配置文件
        new_table_signature = self._get_table_signature(field_configs)
        
        # 获取数据库中所有真实存在的表
        with self.engine.connect() as conn:
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """))
            db_tables = [row[0] for row in result]
        
        # 优先从配置文件中获取表类型信息
        all_schemas = self._load_all_table_schemas()
        
        # 首先尝试匹配相同类型的表
        for table_name in db_tables:
            schema = all_schemas.get(table_name, {})
            if schema.get('type') == table_type:
                existing_signature = self._get_table_signature_from_db(table_name)
                if existing_signature and self._compare_signatures(new_table_signature, existing_signature):
                    return table_name
        
        # 如果没有找到相同类型的表，尝试匹配其他类型的表
        for table_name in db_tables:
            existing_signature = self._get_table_signature_from_db(table_name)
            if existing_signature and self._compare_signatures(new_table_signature, existing_signature):
                return table_name
        
        return None
    
    def _get_table_signature_from_db(self, table_name: str) -> Optional[List[tuple]]:
        """从数据库获取表的字段签名"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = :table_name AND table_schema = 'public'
                    ORDER BY column_name
                """), {"table_name": table_name})
                
                signature = []
                for row in result:
                    col_name = row[0]
                    data_type = row[1]
                    # 跳过系统字段
                    if col_name in ['id', 'created_at', 'updated_at', 'import_batch', 'code']:
                        continue
                    normalized_type = self._normalize_data_type(data_type)
                    signature.append((col_name.lower(), normalized_type))
                
                return sorted(signature)
        except Exception as e:
            print(f"从数据库获取表 {table_name} 的签名失败: {e}")
            return None
    
    def _get_table_signature(self, field_configs: List[Dict[str, Any]]) -> List[tuple]:
        """
        获取表的字段签名（用于比较）
        返回: [(字段名, 数据类型), ...] 按字段名排序
        """
        signature = []
        for field in field_configs:
            target_field = field.get('targetField', '')
            data_type = field.get('dataType', 'VARCHAR')
            if target_field:
                # 标准化类型名称
                normalized_type = self._normalize_data_type(data_type)
                signature.append((target_field.lower(), normalized_type))
        
        # 按字段名排序，确保比较时顺序一致
        return sorted(signature)
    
    def _get_table_signature_from_schema(self, schema: Dict) -> List[tuple]:
        """
        从schema配置中获取字段签名
        """
        signature = []
        fields = schema.get('fields', [])
        
        for field in fields:
            field_name = field.get('name', '')
            data_type = field.get('type', 'VARCHAR')
            
            # 跳过系统字段
            if field_name in ['id', 'created_at', 'updated_at', 'import_batch']:
                continue
            
            if field_name:
                normalized_type = self._normalize_data_type(data_type)
                signature.append((field_name.lower(), normalized_type))
        
        return sorted(signature)
    
    def _normalize_data_type(self, data_type: str) -> str:
        """
        标准化数据类型名称
        """
        type_mapping = {
            'VARCHAR': 'STRING',
            'CHAR': 'STRING',
            'TEXT': 'STRING',
            'INTEGER': 'INTEGER',
            'INT': 'INTEGER',
            'BIGINT': 'INTEGER',
            'DECIMAL': 'DECIMAL',
            'NUMERIC': 'DECIMAL',
            'FLOAT': 'DECIMAL',
            'DOUBLE': 'DECIMAL',
            'DATE': 'DATE',
            'DATETIME': 'DATETIME',
            'TIMESTAMP': 'DATETIME',
            'BOOLEAN': 'BOOLEAN',
            'BOOL': 'BOOLEAN'
        }
        
        upper_type = data_type.upper()
        return type_mapping.get(upper_type, upper_type)
    
    def _compare_signatures(self, sig1: List[tuple], sig2: List[tuple]) -> bool:
        """
        比较两个表签名是否100%匹配
        """
        if len(sig1) != len(sig2):
            return False
        
        for i in range(len(sig1)):
            if sig1[i] != sig2[i]:
                return False
        
        return True
    
    def _table_exists_in_db(self, table_name: str) -> bool:
        """
        检查表是否真实存在于数据库
        """
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(f"""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = '{table_name}'
                    )
                """))
                return result.scalar()
        except Exception as e:
            print(f"检查表存在性失败: {e}")
            return False
    
    def _load_all_table_schemas(self) -> Dict[str, Dict]:
        """
        加载所有表的结构配置
        """
        try:
            if os.path.exists(self.schema_file):
                with open(self.schema_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('tables', {})
        except Exception as e:
            print(f"加载表结构配置失败: {e}")
        
        return {}
    
    def _create_new_table(self, table_name: str, 
                          field_configs: List[Dict[str, Any]],
                          table_type: str = "master",
                          parent_table: Optional[str] = None,
                          foreign_keys: Optional[List[Dict[str, Any]]] = None):
        """
        创建新表
        """
        # 再次检查表是否存在，避免尝试创建已存在的表
        if self._table_exists_in_db(table_name):
            print(f"表 {table_name} 已存在，跳过创建步骤")
            return
        
        # 构建列定义
        columns = []
        foreign_key_constraints = []
        
        # 根据表类型添加主键
        if table_type == "dictionary":
            columns.append(Column('code', String(50), primary_key=True))
        else:
            columns.append(Column('id', Integer, primary_key=True, autoincrement=True))
        
        # 如果是子表，添加外键字段
        if table_type == "child" and parent_table:
            has_parent_fk = foreign_keys and any(
                fk.get('reference_table') == parent_table for fk in foreign_keys
            )
            
            if not has_parent_fk:
                fk_field = f"{parent_table}_id" if not parent_table.endswith('_basic') else "teacher_id"
                columns.append(Column(fk_field, Integer, nullable=False))
                foreign_key_constraints.append({
                    'field': fk_field,
                    'reference_table': parent_table,
                    'reference_field': 'id',
                    'on_delete': 'CASCADE'
                })
        
        # 根据字段配置添加列
        for field in field_configs:
            target_field = field.get('targetField', '')
            data_type = field.get('dataType', 'VARCHAR')
            is_fk = field.get('foreign_key', False)
            
            if not target_field or target_field in ['id', 'code']:
                continue
            
            # 根据数据类型创建列
            col = self._create_column(field, target_field, data_type)
            columns.append(col)
            
            # 记录外键约束
            if is_fk and foreign_keys:
                for fk in foreign_keys:
                    if fk.get('field') == target_field:
                        foreign_key_constraints.append(fk)
        
        # 添加系统字段
        columns.append(Column('created_at', DateTime, default=datetime.now))
        columns.append(Column('updated_at', DateTime, default=datetime.now, onupdate=datetime.now))
        
        if table_type != "dictionary":
            columns.append(Column('import_batch', String(50)))
        
        # 创建表
        with self.engine.connect() as conn:
            # 创建新表
            table = Table(table_name, self.metadata, *columns)
            table.create(self.engine)
            
            # 创建外键约束
            for fk in foreign_key_constraints:
                # 检查引用的表是否真实存在
                reference_table = fk['reference_table']
                if not self._table_exists_in_db(reference_table):
                    print(f"警告: 引用的表 {reference_table} 不存在，跳过外键约束创建")
                    continue
                
                fk_name = f"fk_{table_name}_{fk['field']}"
                on_delete = f"ON DELETE {fk.get('on_delete', 'RESTRICT')}"
                on_update = f"ON UPDATE {fk.get('on_update', 'RESTRICT')}"
                
                sql = f"""
                ALTER TABLE {table_name} 
                ADD CONSTRAINT {fk_name} 
                FOREIGN KEY ({fk['field']}) 
                REFERENCES {reference_table}({fk['reference_field']}) 
                {on_delete} {on_update}
                """
                try:
                    conn.execute(text(sql))
                    print(f"成功创建外键约束: {fk_name}")
                except Exception as e:
                    print(f"创建外键约束失败: {e}")
                    # 外键创建失败不阻止表创建
            
            # 创建索引和唯一约束
            for field in field_configs:
                target_field = field.get('targetField', '')
                if not target_field or target_field in ['id', 'code']:
                    continue
                
                if field.get('indexed', False):
                    index_name = f"idx_{table_name}_{target_field}"
                    conn.execute(text(
                        f"CREATE INDEX {index_name} ON {table_name} ({target_field})"
                    ))
                
                if field.get('unique', False):
                    constraint_name = f"uq_{table_name}_{target_field}"
                    conn.execute(text(
                        f"ALTER TABLE {table_name} ADD CONSTRAINT {constraint_name} UNIQUE ({target_field})"
                    ))
            
            conn.commit()
    
    def _create_column(self, field: Dict, target_field: str, data_type: str) -> Column:
        """
        根据字段配置创建SQLAlchemy列
        """
        nullable = not field.get('required', False)
        
        if data_type == 'INTEGER':
            return Column(target_field, Integer, nullable=nullable)
        elif data_type == 'DECIMAL':
            precision = field.get('precision', 10)
            scale = field.get('scale', 2)
            return Column(target_field, Numeric(precision, scale), nullable=nullable)
        elif data_type == 'DATE':
            return Column(target_field, Date, nullable=nullable)
        elif data_type == 'DATETIME':
            return Column(target_field, DateTime, nullable=nullable)
        elif data_type == 'BOOLEAN':
            return Column(target_field, Boolean, nullable=nullable)
        elif data_type == 'TEXT':
            return Column(target_field, Text, nullable=nullable)
        else:  # VARCHAR
            length = field.get('length', 255)
            return Column(target_field, String(length), nullable=nullable)

    def _convert_date_format(self, value: Any) -> str:
        """
        将各种日期格式转换为标准格式 YYYY-MM-DD
        支持：2001-01-01, 2001-1-1, 2001/01/01, 2001/1/1, 2001年01月01日, 2001年1月1日
        """
        if value is None:
            return None
        
        value_str = str(value).strip()
        if not value_str:
            return None
        
        try:
            # 尝试解析各种日期格式
            import re
            
            # 匹配 2001-01-01 或 2001-1-1
            if re.match(r'^\d{4}-\d{1,2}-\d{1,2}$', value_str):
                year, month, day = value_str.split('-')
                return f"{year}-{int(month):02d}-{int(day):02d}"
            
            # 匹配 2001/01/01 或 2001/1/1
            elif re.match(r'^\d{4}/\d{1,2}/\d{1,2}$', value_str):
                year, month, day = value_str.split('/')
                return f"{year}-{int(month):02d}-{int(day):02d}"
            
            # 匹配 2001年01月01日 或 2001年1月1日
            elif re.match(r'^\d{4}年\d{1,2}月\d{1,2}日$', value_str):
                match = re.match(r'^(\d{4})年(\d{1,2})月(\d{1,2})日$', value_str)
                if match:
                    year, month, day = match.groups()
                    return f"{year}-{int(month):02d}-{int(day):02d}"
            
            # 如果已经是标准格式，直接返回
            elif re.match(r'^\d{4}-\d{2}-\d{2}$', value_str):
                return value_str
            
            # 尝试用 datetime 解析
            else:
                for fmt in ['%Y-%m-%d', '%Y/%m/%d', '%Y年%m月%d日', '%Y-%m-%d %H:%M:%S', '%Y/%m/%d %H:%M:%S']:
                    try:
                        dt = datetime.strptime(value_str, fmt)
                        return dt.strftime('%Y-%m-%d')
                    except ValueError:
                        continue
            
            # 如果都无法解析，返回原值
            return value_str
            
        except Exception as e:
            print(f"日期格式转换失败: {value}, 错误: {e}")
            return value_str
    
    def _insert_data_with_relations(self, 
                                   table_name: str, 
                                   field_configs: List[Dict[str, Any]], 
                                   data: List[Dict[str, Any]],
                                   table_type: str = "master",
                                   parent_table: Optional[str] = None) -> tuple:
        """批量插入数据，处理外键关联"""
        if not data:
            print(f"_insert_data_with_relations: 数据为空，返回 0")
            return 0, []
        
        # 构建字段映射
        field_mapping = {}
        for field in field_configs:
            source = field.get('sourceField', '')
            target = field.get('targetField', '')
            if source and target:
                field_mapping[source] = target
        
        print(f"_insert_data_with_relations: 字段映射: {field_mapping}")
        print(f"_insert_data_with_relations: 数据总行数: {len(data)}")
        
        # 如果是子表，需要处理外键关联和姓名自动填充
        parent_id_map = {}
        parent_name_map = {}
        if table_type == "child" and parent_table:
            # 查找父表的业务主键映射
            parent_id_map = self._get_parent_id_map(parent_table)
            parent_name_map = self._get_parent_name_map(parent_table)
            print(f"_insert_data_with_relations: 父表ID映射: {parent_id_map}")
            print(f"_insert_data_with_relations: 父表姓名映射: {parent_name_map}")
        
        # 准备插入数据
        inserted_count = 0
        skipped_count = 0
        errors = []
        batch_size = 1000
        
        with self.engine.connect() as conn:
            for i in range(0, len(data), batch_size):
                batch = data[i:i + batch_size]
                print(f"_insert_data_with_relations: 处理批次 {i//batch_size + 1}, 批次大小: {len(batch)}")
                
                for row_idx, row in enumerate(batch):
                    # 转换数据
                    insert_data = {}
                    print(f"_insert_data_with_relations: 处理第 {i + row_idx + 1} 行数据: {row}")
                    
                    # 获取身份证号码（用于后续关联）
                    id_card_value = None
                    for source_field, target_field in field_mapping.items():
                        if target_field == '身份证号码':
                            id_card_value = row.get(source_field)
                            break
                    
                    for source_field, target_field in field_mapping.items():
                        value = row.get(source_field)
                        print(f"_insert_data_with_relations: 字段 {source_field} -> {target_field}, 值: {value}, 类型: {type(value)}")

                        # 如果姓名字段为空，尝试从主表获取
                        if target_field == '姓名' and (value is None or str(value).strip() == ''):
                            if id_card_value and id_card_value in parent_name_map:
                                value = parent_name_map[id_card_value]
                                print(f"_insert_data_with_relations: 从主表获取姓名: {value}")

                        # 学历类型和学历字段转换为字符串，以便与字典表关联
                        if target_field in ['学历类型', '学历'] and value is not None:
                            value = str(int(value)) if isinstance(value, (int, float)) else str(value)
                            print(f"_insert_data_with_relations: 将 {target_field} 转换为字符串: {value}")

                        # 日期字段格式转换：将 2001/1/1 或 2001年1月1日 转换为 2001-01-01
                        if value is not None and target_field in ['出生日期', '参加工作日期', '进入本单位日期', '入党日期', '毕业日期', '档案出生日期']:
                            value = self._convert_date_format(value)
                            print(f"_insert_data_with_relations: 日期字段 {target_field} 转换后: {value}")

                        if value is not None and str(value).strip() != '':
                            insert_data[target_field] = value
                        else:
                            print(f"_insert_data_with_relations: 字段 {source_field} 值为空或为None，跳过")
                    
                    # 如果是字典表，添加code字段
                    if table_type == "dictionary":
                        # 尝试从数据中获取code值
                        code_value = None
                        # 检查是否有code字段
                        for source_field, target_field in field_mapping.items():
                            if target_field == 'code':
                                code_value = row.get(source_field)
                                break
                        # 如果没有code字段，尝试使用第一个字段的值作为code
                        if not code_value:
                            if field_mapping:
                                first_source_field = next(iter(field_mapping.keys()))
                                code_value = row.get(first_source_field)
                        # 如果仍然没有code值，使用随机值
                        if not code_value:
                            import uuid
                            code_value = str(uuid.uuid4())[:8]
                        insert_data['code'] = code_value
                        print(f"_insert_data_with_relations: 字典表添加code字段: {code_value}")
                    
                    # 如果是子表，处理外键关联
                    if table_type == "child" and parent_table and parent_id_map:
                        # 尝试通过业务主键查找父表ID
                        business_key = self._find_business_key(row, field_configs)
                        print(f"_insert_data_with_relations: 查找业务主键: {business_key}")
                        if business_key and business_key in parent_id_map:
                            fk_field = f"{parent_table}_id" if not parent_table.endswith('_basic') else "teacher_id"
                            insert_data[fk_field] = parent_id_map[business_key]
                            print(f"_insert_data_with_relations: 添加外键 {fk_field} = {parent_id_map[business_key]}")
                        else:
                            error_msg = f"第 {i + row_idx + 1} 行数据无法找到父表关联ID，父表: {parent_table}"
                            print(f"_insert_data_with_relations: {error_msg}")
                            errors.append(error_msg)
                            skipped_count += 1
                            continue  # 跳过这条数据，避免事务失败
                    
                    print(f"_insert_data_with_relations: 处理后的数据: {insert_data}")
                    
                    if insert_data:
                        # 构建INSERT语句
                        columns = list(insert_data.keys())
                        print(f"_insert_data_with_relations: 插入的列: {columns}")
                        
                        sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join([':' + c for c in columns])})"
                        print(f"_insert_data_with_relations: SQL语句: {sql}")
                        
                        try:
                            conn.execute(text(sql), insert_data)
                            inserted_count += 1
                            print(f"_insert_data_with_relations: 插入成功，累计插入: {inserted_count}")
                        except Exception as e:
                            error_msg = f"第 {i + row_idx + 1} 行数据插入失败: {str(e)}"
                            print(f"_insert_data_with_relations: {error_msg}")
                            errors.append(error_msg)
                    else:
                        skipped_count += 1
                        print(f"_insert_data_with_relations: 数据为空，跳过插入，累计跳过: {skipped_count}")
                
                conn.commit()
                print(f"_insert_data_with_relations: 提交批次，当前插入: {inserted_count}, 跳过: {skipped_count}, 错误: {len(errors)}")
        
        print(f"_insert_data_with_relations: 处理完成，总计插入: {inserted_count}, 跳过: {skipped_count}, 错误: {len(errors)}")
        return inserted_count, errors
    
    def _upsert_data_with_relations(self, 
                                   table_name: str, 
                                   field_configs: List[Dict[str, Any]], 
                                   data: List[Dict[str, Any]],
                                   table_type: str = "master",
                                   parent_table: Optional[str] = None) -> tuple:
        """
        智能插入/更新数据，处理外键关联
        返回: (插入条数, 更新条数, 错误信息列表)
        """
        if not data:
            print(f"_upsert_data_with_relations: 数据为空，返回 (0, 0, [])")
            return 0, 0, []
        
        # 构建字段映射
        field_mapping = {}
        unique_fields = []
        
        for field in field_configs:
            source = field.get('sourceField', '')
            target = field.get('targetField', '')
            if source and target:
                field_mapping[source] = target
            
            # 收集唯一性字段
            if field.get('unique', False) and target:
                unique_fields.append(target)
        
        print(f"_upsert_data_with_relations: 字段映射: {field_mapping}")
        print(f"_upsert_data_with_relations: 唯一性字段: {unique_fields}")
        print(f"_upsert_data_with_relations: 数据总行数: {len(data)}")
        
        # 如果没有配置唯一性字段，尝试使用常见的业务主键
        if not unique_fields:
            for source, target in field_mapping.items():
                if any(keyword in source for keyword in ['身份证', '编号', 'code', 'id_card', '工号', '学号']):
                    unique_fields.append(target)
                    break
            print(f"_upsert_data_with_relations: 自动添加唯一性字段: {unique_fields}")
        
        # 如果是子表，需要处理外键关联和姓名自动填充
        parent_id_map = {}
        parent_name_map = {}
        if table_type == "child" and parent_table:
            parent_id_map = self._get_parent_id_map(parent_table)
            parent_name_map = self._get_parent_name_map(parent_table)
            print(f"_upsert_data_with_relations: 父表ID映射: {parent_id_map}")
            print(f"_upsert_data_with_relations: 父表姓名映射: {parent_name_map}")
        
        # 获取现有数据（用于判断是否存在）
        existing_records = self._get_existing_records(table_name, unique_fields)
        print(f"_upsert_data_with_relations: 现有记录数: {len(existing_records)}")
        
        # 准备插入/更新数据
        inserted_count = 0
        updated_count = 0
        skipped_count = 0
        errors = []
        batch_size = 1000
        
        with self.engine.connect() as conn:
            for i in range(0, len(data), batch_size):
                batch = data[i:i + batch_size]
                print(f"_upsert_data_with_relations: 处理批次 {i//batch_size + 1}, 批次大小: {len(batch)}")
                
                for row_idx, row in enumerate(batch):
                    # 转换数据
                    row_data = {}
                    print(f"_upsert_data_with_relations: 处理第 {i + row_idx + 1} 行数据: {row}")
                    
                    # 获取身份证号码（用于后续关联）
                    id_card_value = None
                    for source_field, target_field in field_mapping.items():
                        if target_field == '身份证号码':
                            id_card_value = row.get(source_field)
                            break
                    
                    for source_field, target_field in field_mapping.items():
                        value = row.get(source_field)
                        print(f"_upsert_data_with_relations: 字段 {source_field} -> {target_field}, 值: {value}, 类型: {type(value)}")

                        # 如果姓名字段为空，尝试从主表获取
                        if target_field == '姓名' and (value is None or str(value).strip() == ''):
                            if id_card_value and id_card_value in parent_name_map:
                                value = parent_name_map[id_card_value]
                                print(f"_upsert_data_with_relations: 从主表获取姓名: {value}")

                        # 学历类型和学历字段转换为字符串，以便与字典表关联
                        if target_field in ['学历类型', '学历'] and value is not None:
                            value = str(int(value)) if isinstance(value, (int, float)) else str(value)
                            print(f"_upsert_data_with_relations: 将 {target_field} 转换为字符串: {value}")

                        # 日期字段格式转换：将 2001/1/1 或 2001年1月1日 转换为 2001-01-01
                        if value is not None and target_field in ['出生日期', '参加工作日期', '进入本单位日期', '入党日期', '毕业日期', '档案出生日期']:
                            value = self._convert_date_format(value)
                            print(f"_upsert_data_with_relations: 日期字段 {target_field} 转换后: {value}")

                        if value is not None and str(value).strip() != '':
                            row_data[target_field] = value
                        else:
                            print(f"_upsert_data_with_relations: 字段 {source_field} 值为空或为None，跳过")
                    
                    # 如果是字典表，添加code字段
                    if table_type == "dictionary":
                        # 尝试从数据中获取code值
                        code_value = None
                        # 检查是否有code字段
                        for source_field, target_field in field_mapping.items():
                            if target_field == 'code':
                                code_value = row.get(source_field)
                                break
                        # 如果没有code字段，尝试使用第一个字段的值作为code
                        if not code_value:
                            if field_mapping:
                                first_source_field = next(iter(field_mapping.keys()))
                                code_value = row.get(first_source_field)
                        # 如果仍然没有code值，使用随机值
                        if not code_value:
                            import uuid
                            code_value = str(uuid.uuid4())[:8]
                        row_data['code'] = code_value
                        print(f"_upsert_data_with_relations: 字典表添加code字段: {code_value}")
                    
                    # 如果是子表，处理外键关联
                    if table_type == "child" and parent_table and parent_id_map:
                        business_key = self._find_business_key(row, field_configs)
                        print(f"_upsert_data_with_relations: 查找业务主键: {business_key}")
                        if business_key and business_key in parent_id_map:
                            fk_field = f"{parent_table}_id" if not parent_table.endswith('_basic') else "teacher_id"
                            row_data[fk_field] = parent_id_map[business_key]
                            print(f"_upsert_data_with_relations: 添加外键 {fk_field} = {parent_id_map[business_key]}")
                        else:
                            error_msg = f"第 {i + row_idx + 1} 行数据无法找到父表关联ID，父表: {parent_table}"
                            print(f"_upsert_data_with_relations: {error_msg}")
                            errors.append(error_msg)
                            skipped_count += 1
                            continue  # 跳过这条数据，避免事务失败
                    
                    print(f"_upsert_data_with_relations: 处理后的数据: {row_data}")
                    
                    if not row_data:
                        skipped_count += 1
                        print(f"_upsert_data_with_relations: 数据为空，跳过处理，累计跳过: {skipped_count}")
                        continue
                    
                    # 判断是插入还是更新
                    existing_id = None
                    if unique_fields:
                        # 构建唯一键值
                        unique_key_values = tuple(row_data.get(f) for f in unique_fields if f in row_data)
                        print(f"_upsert_data_with_relations: 唯一键值: {unique_key_values}, 唯一性字段长度: {len(unique_fields)}")
                        if len(unique_key_values) == len(unique_fields):
                            existing_id = existing_records.get(unique_key_values)
                            print(f"_upsert_data_with_relations: 现有ID: {existing_id}")
                    
                    try:
                        if existing_id:
                            # 更新现有记录
                            print(f"_upsert_data_with_relations: 更新现有记录，ID: {existing_id}")
                            self._update_record(conn, table_name, existing_id, row_data)
                            updated_count += 1
                            print(f"_upsert_data_with_relations: 更新成功，累计更新: {updated_count}")
                        else:
                            # 插入新记录
                            print(f"_upsert_data_with_relations: 插入新记录")
                            self._insert_record(conn, table_name, row_data)
                            inserted_count += 1
                            print(f"_upsert_data_with_relations: 插入成功，累计插入: {inserted_count}")
                            
                            # 更新现有记录缓存
                            if unique_fields and 'id' in row_data:
                                unique_key_values = tuple(row_data.get(f) for f in unique_fields)
                                existing_records[unique_key_values] = row_data['id']
                                print(f"_upsert_data_with_relations: 更新现有记录缓存: {unique_key_values} -> {row_data['id']}")
                    except Exception as e:
                        error_msg = f"第 {i + row_idx + 1} 行数据处理失败: {str(e)}"
                        print(f"_upsert_data_with_relations: {error_msg}")
                        errors.append(error_msg)
                
                conn.commit()
                print(f"_upsert_data_with_relations: 提交批次，当前插入: {inserted_count}, 更新: {updated_count}, 跳过: {skipped_count}, 错误: {len(errors)}")
        
        print(f"_upsert_data_with_relations: 处理完成，总计插入: {inserted_count}, 更新: {updated_count}, 跳过: {skipped_count}, 错误: {len(errors)}")
        return inserted_count, updated_count, errors
    
    def _get_existing_records(self, table_name: str, unique_fields: List[str]) -> Dict[tuple, int]:
        """
        获取现有记录的唯一键到ID的映射
        """
        existing_records = {}
        
        if not unique_fields:
            return existing_records
        
        try:
            with self.engine.connect() as conn:
                # 查询现有记录的唯一键和ID
                fields_str = ', '.join(unique_fields + ['id'])
                result = conn.execute(text(f"SELECT {fields_str} FROM {table_name}"))
                
                for row in result:
                    # 构建唯一键值元组
                    key_values = tuple(getattr(row, f) for f in unique_fields)
                    existing_records[key_values] = row.id
        except Exception as e:
            print(f"获取现有记录失败: {e}")
        
        return existing_records
    
    def _update_record(self, conn, table_name: str, record_id: int, data: Dict[str, Any]):
        """
        更新现有记录
        """
        # 移除id字段（不能更新主键）
        update_data = {k: v for k, v in data.items() if k != 'id'}
        
        if not update_data:
            return
        
        # 构建UPDATE语句
        set_clauses = [f"{k} = :{k}" for k in update_data.keys()]
        update_data['id'] = record_id
        
        sql = f"UPDATE {table_name} SET {', '.join(set_clauses)} WHERE id = :id"
        conn.execute(text(sql), update_data)
    
    def _insert_record(self, conn, table_name: str, data: Dict[str, Any]):
        """
        插入新记录
        """
        columns = list(data.keys())
        sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join([':' + c for c in columns])})"
        conn.execute(text(sql), data)
    
    def _get_parent_id_map(self, parent_table: str) -> Dict[str, int]:
        """获取父表的业务主键到ID的映射"""
        id_map = {}
        try:
            with self.engine.connect() as conn:
                # 查询父表的所有字段
                result = conn.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = :table_name AND table_schema = 'public'
                """), {"table_name": parent_table})
                columns = [row[0] for row in result]
                print(f"_get_parent_id_map: 父表 {parent_table} 的字段: {columns}")
                
                # 查找业务主键字段（身份证号码、id_card、code等）
                business_key_column = None
                for col in columns:
                    if col in ['身份证号码', '身份证号']:
                        business_key_column = col
                        break
                    elif col == 'id_card':
                        business_key_column = col
                        break
                    elif col == 'code':
                        business_key_column = col
                        break
                
                if business_key_column:
                    # 查询父表的ID和业务主键
                    result = conn.execute(text(f"SELECT id, \"{business_key_column}\" FROM {parent_table}"))
                    for row in result:
                        business_key = getattr(row, business_key_column)
                        if business_key:
                            id_map[str(business_key)] = row.id
                    print(f"_get_parent_id_map: 获取到 {len(id_map)} 条父表映射")
                else:
                    print(f"_get_parent_id_map: 未找到业务主键字段")
        except Exception as e:
            print(f"获取父表映射失败: {e}")
        return id_map
    
    def _get_parent_name_map(self, parent_table: str) -> Dict[str, str]:
        """获取父表的业务主键到姓名的映射"""
        name_map = {}
        try:
            with self.engine.connect() as conn:
                # 查询父表的所有字段
                result = conn.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = :table_name AND table_schema = 'public'
                """), {"table_name": parent_table})
                columns = [row[0] for row in result]
                
                # 查找业务主键字段和姓名字段
                business_key_column = None
                name_column = None
                
                for col in columns:
                    if col in ['身份证号码', '身份证号']:
                        business_key_column = col
                    elif col == 'id_card':
                        business_key_column = col
                    elif col in ['姓名', 'name']:
                        name_column = col
                
                if business_key_column and name_column:
                    # 查询主表的业务主键和姓名
                    result = conn.execute(text(f'SELECT "{business_key_column}", "{name_column}" FROM {parent_table} WHERE "{business_key_column}" IS NOT NULL'))
                    for row in result:
                        business_key = getattr(row, business_key_column)
                        name = getattr(row, name_column)
                        if business_key:
                            name_map[str(business_key)] = name
                    print(f"_get_parent_name_map: 获取到 {len(name_map)} 条姓名映射")
        except Exception as e:
            print(f"获取父表姓名映射失败: {e}")
        return name_map
    
    def _find_business_key(self, row: Dict[str, Any], field_configs: List[Dict[str, Any]]) -> Optional[str]:
        """从数据行中查找业务主键值"""
        # 常见的业务主键字段名
        business_key_fields = ['身份证号码', '身份证号', 'id_card', '编号', 'code', '工号', '学号']
        
        for field in field_configs:
            source_field = field.get('sourceField', '')
            if source_field in business_key_fields or any(bk in source_field for bk in business_key_fields):
                value = row.get(source_field)
                if value:
                    return str(value)
        
        return None
    
    def _update_schema_config(self, 
                             table_name: str, 
                             field_configs: List[Dict[str, Any]],
                             table_type: str = "master",
                             parent_table: Optional[str] = None,
                             foreign_keys: Optional[List[Dict[str, Any]]] = None):
        """更新配置文件，实现原子操作保存"""
        try:
            # 数据验证：检查关联表是否存在
            self._validate_relation_tables(field_configs)
            
            # 读取现有配置
            config = self._read_json_file(self.schema_file)
            if not config:
                config = {"tables": {}, "dictionaries": {}, "mappings": [], "relationships": {}}
            
            # 构建表结构定义
            table_schema = {
                "name": table_name,
                "type": table_type,
                "title": self._generate_table_title(table_name),
                "description": f"{self._generate_table_title(table_name)}表",
                "primary_key": "code" if table_type == "dictionary" else "id",
                "fields": []
            }
            
            # 子表添加父表关联
            if table_type == "child" and parent_table:
                table_schema["parent_table"] = parent_table
                if foreign_keys:
                    table_schema["foreign_keys"] = foreign_keys
            
            # 添加字段定义
            for field in field_configs:
                field_def = {
                    "name": field.get('targetField', ''),
                    "source_name": field.get('sourceField', ''),
                    "type": field.get('dataType', 'VARCHAR'),
                    "required": field.get('required', False),
                    "unique": field.get('unique', False),
                    "indexed": field.get('indexed', False),
                    "label": field.get('sourceField', ''),
                    "description": field.get('description', ''),
                    "relation_type": field.get('relation_type', 'none'),
                    "relation_table": field.get('relation_table', ''),
                    "relation_display_field": field.get('relation_display_field', 'name')
                }
                
                # 根据类型添加额外属性
                if field_def["type"] == 'VARCHAR':
                    field_def["length"] = field.get('length', 255)
                elif field_def["type"] == 'DECIMAL':
                    field_def["precision"] = field.get('precision', 10)
                    field_def["scale"] = field.get('scale', 2)
                
                # 标记外键字段
                if field.get('foreign_key', False):
                    field_def["foreign_key"] = True
                
                # 标记字典关联
                if field.get('dictionary'):
                    field_def["dictionary"] = field.get('dictionary')
                
                table_schema["fields"].append(field_def)
            
            # 更新tables部分
            config["tables"][table_name] = table_schema
            
            # 更新mappings部分
            for field in field_configs:
                mapping = {
                    "table": table_name,
                    "source_field": field.get('sourceField', ''),
                    "target_field": field.get('targetField', ''),
                    "data_type": field.get('dataType', 'VARCHAR'),
                    "relation_type": field.get('relation_type', 'none'),
                    "relation_table": field.get('relation_table', ''),
                    "relation_display_field": field.get('relation_display_field', 'name'),
                    "created_at": datetime.now().isoformat()
                }
                
                # 检查是否已存在相同的映射
                existing = next((m for m in config["mappings"] 
                               if m["table"] == table_name and m["source_field"] == mapping["source_field"]), None)
                if existing:
                    existing.update(mapping)
                else:
                    config["mappings"].append(mapping)
            
            # 原子操作保存：同时更新所有配置文件
            # 1. 保存merged_schema_mappings.json
            self._write_json_file(self.schema_file, config)
            
            # 2. 保存table_schemas.json
            self._update_table_schemas(table_name, table_schema)
            
            # 3. 保存field_mappings.json
            self._update_field_mappings(table_name, field_configs)
            
        except Exception as e:
            print(f"更新schema配置失败: {e}")
            raise
    
    def _update_navigation_config(self, 
                                 table_name: str, 
                                 module_id: str, 
                                 module_name: str,
                                 field_configs: List[Dict[str, Any]],
                                 table_type: str = "master",
                                 parent_table: Optional[str] = None,
                                 chinese_title: str = "",
                                 sub_module_id: str = "",
                                 sub_module_name: str = ""):
        """更新navigation.json配置文件，根据表类型组织导航"""
        try:
            # 读取现有配置
            config = self._read_json_file(self.navigation_file)
            if not config:
                config = {"modules": []}
            
            # 查找目标模块
            target_module = None
            for module in config["modules"]:
                if module.get("id") == module_id:
                    target_module = module
                    break
            
            # 如果模块不存在，创建新模块
            if not target_module:
                target_module = {
                    "id": module_id,
                    "title": module_name,
                    "icon": "Folder",
                    "path": f"/{module_id}",
                    "type": "module",
                    "children": []
                }
                config["modules"].append(target_module)
            
            # 根据表类型创建节点
            node_id = f"{module_id}-{table_name}"
            # 优先使用中文标题（从文件名提取），其次根据表名生成
            node_title = chinese_title if chinese_title else self._generate_table_title(table_name)
            
            # 确定节点应该放在哪里
            # 如果有子模块ID，优先放在子模块下
            if sub_module_id:
                # 在子模块下创建节点
                self._create_node_in_submodule(
                    target_module, sub_module_id, sub_module_name,
                    node_id, node_title, table_name, module_id, table_type
                )
            elif table_type == "child" and parent_table:
                # 如果是子表，放在父表节点下
                parent_node = None
                for child in target_module.get("children", []):
                    if child.get("table_name") == parent_table:
                        parent_node = child
                        break
                
                if parent_node:
                    # 在父表节点下创建子节点
                    if "children" not in parent_node:
                        parent_node["children"] = []
                    
                    new_node = {
                        "id": node_id,
                        "title": node_title,
                        "icon": "Document",
                        "path": f"/{module_id}/{parent_table}/{table_name}",
                        "type": "component",
                        "component": "DataTable",
                        "api_endpoint": f"/api/data/{table_name}",
                        "table_name": table_name,
                        "table_type": table_type,
                        "parent_table": parent_table,
                        "created_at": datetime.now().isoformat()
                    }
                    
                    # 检查节点是否已存在
                    existing = next((n for n in parent_node["children"] 
                                   if n.get("table_name") == table_name), None)
                    if existing:
                        existing.update(new_node)
                    else:
                        parent_node["children"].append(new_node)
                else:
                    # 父表节点不存在，创建在模块下
                    self._create_node_in_module(target_module, node_id, node_title, 
                                              table_name, module_id, table_type, parent_table)
            else:
                # 主表或字典表直接放在模块下
                self._create_node_in_module(target_module, node_id, node_title, 
                                          table_name, module_id, table_type, parent_table)
            
            # 保存配置
            self._write_json_file(self.navigation_file, config)
            
        except Exception as e:
            print(f"更新导航配置失败: {e}")
            raise
    
    def _create_node_in_module(self, module: Dict[str, Any], node_id: str, 
                              node_title: str, table_name: str, module_id: str,
                              table_type: str, parent_table: Optional[str]):
        """在模块下创建节点"""
        new_node = {
            "id": node_id,
            "title": node_title,
            "icon": "Document" if table_type != "dictionary" else "Collection",
            "path": f"/{module_id}/{table_name}",
            "type": "component",
            "component": "DataTable",
            "api_endpoint": f"/api/data/{table_name}",
            "table_name": table_name,
            "table_type": table_type,
            "created_at": datetime.now().isoformat()
        }
        
        if parent_table:
            new_node["parent_table"] = parent_table
        
        # 检查节点是否已存在
        existing = next((n for n in module.get("children", []) 
                        if n.get("table_name") == table_name), None)
        if existing:
            existing.update(new_node)
        else:
            if "children" not in module:
                module["children"] = []
            module["children"].append(new_node)
    
    def _create_node_in_submodule(self, module: Dict[str, Any], sub_module_id: str,
                                  sub_module_name: str, node_id: str, 
                                  node_title: str, table_name: str, module_id: str,
                                  table_type: str):
        """在子模块下创建节点"""
        # 查找子模块
        sub_module = None
        for child in module.get("children", []):
            if child.get("id") == sub_module_id:
                sub_module = child
                break
        
        # 如果子模块不存在，创建它
        if not sub_module:
            sub_module = {
                "id": sub_module_id,
                "title": sub_module_name,
                "icon": "Folder",
                "path": f"/{module_id}/{sub_module_id}",
                "type": "module",
                "children": []
            }
            if "children" not in module:
                module["children"] = []
            module["children"].append(sub_module)
        
        # 在子模块下创建数据节点
        new_node = {
            "id": node_id,
            "title": node_title,
            "icon": "Document" if table_type != "dictionary" else "Collection",
            "path": f"/{module_id}/{sub_module_id}/{table_name}",
            "type": "component",
            "component": "DataTable",
            "api_endpoint": f"/api/data/{table_name}",
            "table_name": table_name,
            "table_type": table_type,
            "created_at": datetime.now().isoformat()
        }
        
        # 检查节点是否已存在
        existing = next((n for n in sub_module.get("children", []) 
                        if n.get("table_name") == table_name), None)
        if existing:
            existing.update(new_node)
        else:
            if "children" not in sub_module:
                sub_module["children"] = []
            sub_module["children"].append(new_node)
    
    def _update_relationship_config(self, 
                                   table_name: str, 
                                   table_type: str,
                                   parent_table: Optional[str]):
        """更新表关系配置"""
        try:
            config = self._read_json_file(self.schema_file)
            if not config:
                return
            
            if "relationships" not in config:
                config["relationships"] = {}
            
            # 如果是子表，更新父表的children列表
            if table_type == "child" and parent_table:
                if parent_table not in config["relationships"]:
                    config["relationships"][parent_table] = {"children": [], "dictionaries": []}
                
                if table_name not in config["relationships"][parent_table]["children"]:
                    config["relationships"][parent_table]["children"].append(table_name)
            
            # 保存配置
            self._write_json_file(self.schema_file, config)
            
        except Exception as e:
            print(f"更新关系配置失败: {e}")
    
    def _validate_relation_tables(self, field_configs: List[Dict[str, Any]]):
        """验证关联表是否存在，但允许关联表不存在时继续导入"""
        # 读取现有配置
        config = self._read_json_file(self.schema_file)
        if not config:
            config = {"tables": {}, "dictionaries": {}}
        
        # 收集所有存在的表名
        existing_tables = set(config.get("tables", {}).keys())
        existing_dicts = set(config.get("dictionaries", {}).keys())
        
        # 验证每个字段的关联表
        for field in field_configs:
            relation_type = field.get('relation_type', 'none')
            relation_table = field.get('relation_table', '')
            
            if relation_type != 'none' and relation_table:
                if relation_type == 'to_master' and relation_table not in existing_tables:
                    # 关联表不存在，记录警告但不阻止导入
                    print(f"警告: 关联表 '{relation_table}' 不存在，将跳过关联处理")
                    # 移除关联配置，避免后续处理出错
                    field['relation_type'] = 'none'
                    field['relation_table'] = ''
                elif relation_type == 'to_dict':
                    # 字典表可能在tables中（实际的数据库字典表）或在dictionaries中（虚拟字典表）
                    if relation_table not in existing_tables and relation_table not in existing_dicts:
                        # 字典表不存在，记录警告但不阻止导入
                        print(f"警告: 字典表 '{relation_table}' 不存在，将跳过字典关联处理")
                        # 移除关联配置，避免后续处理出错
                        field['relation_type'] = 'none'
                        field['relation_table'] = ''
    
    def _update_table_schemas(self, table_name: str, table_schema: Dict[str, Any]):
        """更新table_schemas.json配置文件"""
        # 读取现有配置
        config = self._read_json_file(self.table_schemas_file)
        if not config:
            config = {"tables": {}}
        
        # 更新表结构
        config["tables"][table_name] = table_schema
        
        # 保存配置
        self._write_json_file(self.table_schemas_file, config)
    
    def _update_field_mappings(self, table_name: str, field_configs: List[Dict[str, Any]]):
        """更新field_mappings.json配置文件"""
        # 读取现有配置
        config = self._read_json_file(self.field_mappings_file)
        if not config:
            config = {"configs": [], "global_mappings": {}, "usage_stats": {}}
        
        # 更新字段映射
        for field in field_configs:
            mapping = {
                "table": table_name,
                "source_field": field.get('sourceField', ''),
                "target_field": field.get('targetField', ''),
                "data_type": field.get('dataType', 'VARCHAR'),
                "relation_type": field.get('relation_type', 'none'),
                "relation_table": field.get('relation_table', ''),
                "relation_display_field": field.get('relation_display_field', 'name'),
                "created_at": datetime.now().isoformat()
            }
            
            # 检查是否已存在相同的映射
            existing = next((m for m in config["configs"] 
                           if m["table"] == table_name and m["source_field"] == mapping["source_field"]), None)
            if existing:
                existing.update(mapping)
            else:
                config["configs"].append(mapping)
        
        # 保存配置
        self._write_json_file(self.field_mappings_file, config)
    
    def _generate_table_title(self, table_name: str) -> str:
        """根据表名生成表标题"""
        name_mapping = {
            "teacher_basic": "教师基础信息",
            "teacher_education": "教育经历",
            "teacher_work": "工作经历",
            "teacher_title": "职称变动",
            "education_level": "学历",
            "degree": "学位",
            "title": "职称",
            "title_level": "职称级别",
            "gender": "性别",
            "department": "部门"
        }
        
        return name_mapping.get(table_name, table_name.replace('_', ' ').title())
    
    def _trigger_config_update(self):
        """触发配置更新事件"""
        pass
    
    def _read_json_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """读取JSON文件"""
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return None
        except Exception as e:
            print(f"读取文件失败 {file_path}: {e}")
            return None
    
    def _write_json_file(self, file_path: str, data: Dict[str, Any]):
        """写入JSON文件"""
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"写入文件失败 {file_path}: {e}")
            raise
