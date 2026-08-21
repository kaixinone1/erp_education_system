#!/usr/bin/env python3
"""
通用导入服务 V2 - 支持统一关联规范

特性：
1. 配置化字段映射
2. 智能数据类型推断
3. 自动日期格式转换
4. 自动关联主表（通过身份证号码）
5. 自动关联字典表（通过code）
6. 支持多表查询和统计
"""

import json
import os
import re
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from sqlalchemy import create_engine, Table, Column, MetaData, String, Integer, Float, Date, DateTime, Boolean, Text, Numeric
from sqlalchemy.sql import text


class UniversalImportServiceV2:
    """
    通用导入服务 V2
    
    核心功能：
    - 自动识别字段类型
    - 自动创建表结构（包含系统字段和关联字段）
    - 自动关联主表（通过身份证号码获取teacher_id）
    - 自动关联字典表（通过code获取id和name）
    """
    
    def __init__(self, db_url: str = None, config_path: str = None):
        # 数据库连接
        if db_url is None:
            db_url = os.getenv('DATABASE_URL', 'postgresql://taiping_user:taiping_password@localhost:5432/taiping_education')
        self.engine = create_engine(db_url)
        self.metadata = MetaData()
        
        # 加载配置
        if config_path is None:
            config_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                'config',
                'import_config.json'
            )
        self.config = self._load_config(config_path)
        
        # 系统字段
        self.system_fields = self.config.get('system_fields', {}).get('fields', [])
        
        # 关联规则
        self.relationship_rules = self.config.get('relationship_rules', {})
        
        # 字典表配置
        self.dictionary_config = self.config.get('dictionary_tables', {})
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """加载配置文件"""
        default_config = {
            "field_type_mappings": {"rules": []},
            "validation_rules": {},
            "date_formats": {"auto_convert": True},
            "system_fields": {"fields": []},
            "relationship_rules": {},
            "dictionary_tables": {}
        }
        
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                print(f"配置文件不存在: {config_path}, 使用默认配置")
                return default_config
        except Exception as e:
            print(f"加载配置文件失败: {e}, 使用默认配置")
            return default_config
    
    def import_dictionary(self, table_name: str, data: List[Dict], 
                         code_field: str = "序号", name_field: str = "名称") -> Dict[str, Any]:
        """
        导入字典表
        
        Args:
            table_name: 字典表名（如 dict_position）
            data: 字典数据
            code_field: 数据源中的code字段名
            name_field: 数据源中的name字段名
        
        Returns:
            {"success": True/False, "inserted": 数量, "errors": []}
        """
        try:
            # 1. 创建字典表结构
            self._create_dictionary_table(table_name)
            
            # 2. 处理数据
            processed_data = []
            for row in data:
                code = str(row.get(code_field, '')).strip()
                name = str(row.get(name_field, '')).strip()
                
                if code and name:
                    processed_data.append({
                        'code': code,
                        'name': name,
                        'sort_order': int(code) if code.isdigit() else None,
                        'status': True
                    })
            
            # 3. 插入数据
            inserted_count = self._insert_dictionary_data(table_name, processed_data)
            
            return {
                "success": True,
                "inserted": inserted_count,
                "errors": []
            }
            
        except Exception as e:
            return {
                "success": False,
                "inserted": 0,
                "errors": [str(e)]
            }
    
    def _create_dictionary_table(self, table_name: str):
        """创建字典表结构"""
        import psycopg2
        
        db_url = self.engine.url
        conn_params = {
            'host': db_url.host,
            'database': db_url.database,
            'user': db_url.username,
            'password': db_url.password,
            'port': db_url.port or 5432
        }
        
        conn = psycopg2.connect(**conn_params)
        cursor = conn.cursor()
        
        try:
            # 检查表是否存在
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = %s
                )
            """, (table_name,))
            
            table_exists = cursor.fetchone()[0]
            
            if not table_exists:
                # 创建字典表
                create_sql = f"""
                    CREATE TABLE {table_name} (
                        id SERIAL PRIMARY KEY,
                        code VARCHAR(30) UNIQUE,
                        name VARCHAR(50) NOT NULL,
                        sort_order INTEGER,
                        status BOOLEAN DEFAULT true,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """
                cursor.execute(create_sql)
                conn.commit()
                print(f"创建字典表: {table_name}")
        finally:
            cursor.close()
            conn.close()
    
    def _insert_dictionary_data(self, table_name: str, data: List[Dict]) -> int:
        """插入字典数据"""
        import psycopg2
        
        db_url = self.engine.url
        conn_params = {
            'host': db_url.host,
            'database': db_url.database,
            'user': db_url.username,
            'password': db_url.password,
            'port': db_url.port or 5432
        }
        
        inserted_count = 0
        conn = psycopg2.connect(**conn_params)
        cursor = conn.cursor()
        
        try:
            for row in data:
                # 使用 UPSERT 避免重复
                upsert_sql = f"""
                    INSERT INTO {table_name} (code, name, sort_order, status)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (code) DO UPDATE SET
                        name = EXCLUDED.name,
                        sort_order = EXCLUDED.sort_order
                """
                cursor.execute(upsert_sql, (
                    row['code'],
                    row['name'],
                    row['sort_order'],
                    row['status']
                ))
                inserted_count += 1
            
            conn.commit()
        finally:
            cursor.close()
            conn.close()
        
        return inserted_count
    
    def import_child_table(self, table_name: str, field_configs: List[Dict], 
                          data: List[Dict], table_type: str = "child") -> Dict[str, Any]:
        """
        导入子表（自动关联主表和字典表）
        
        Args:
            table_name: 子表名
            field_configs: 字段配置
            data: 要导入的数据
            table_type: 表类型
        
        Returns:
            {"success": True/False, "inserted": 数量, "errors": []}
        """
        try:
            # 1. 识别需要关联的字段
            dict_fields = self._identify_dictionary_fields(field_configs)
            print(f"识别到字典关联字段: {dict_fields}")
            
            # 2. 创建表结构（包含关联字段）
            self._create_child_table(table_name, field_configs, dict_fields)
            
            # 3. 处理数据（关联主表和字典表）
            processed_data = self._process_child_data(data, field_configs, dict_fields)
            
            # 4. 插入数据
            inserted_count = self._insert_child_data(table_name, processed_data)
            
            return {
                "success": True,
                "inserted": inserted_count,
                "errors": []
            }
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "inserted": 0,
                "errors": [str(e)]
            }
    
    def _identify_dictionary_fields(self, field_configs: List[Dict]) -> List[Dict]:
        """识别需要关联字典表的字段"""
        dict_fields = []
        
        for field in field_configs:
            if field.get('link_to_dictionary'):
                dict_fields.append({
                    'source_field': field['source_field'],
                    'target_field': field['target_field'],
                    'dictionary_table': field.get('dictionary_table', ''),
                    'dictionary_key_field': field.get('dictionary_key_field', 'code'),
                    'dictionary_display_field': field.get('dictionary_display_field', 'name'),
                    'value_mapping': field.get('value_mapping', {})  # 添加值映射配置
                })
        
        return dict_fields
    
    def _create_child_table(self, table_name: str, field_configs: List[Dict], dict_fields: List[Dict]):
        """创建子表结构（包含关联字段）"""
        import psycopg2
        
        db_url = self.engine.url
        conn_params = {
            'host': db_url.host,
            'database': db_url.database,
            'user': db_url.username,
            'password': db_url.password,
            'port': db_url.port or 5432
        }
        
        conn = psycopg2.connect(**conn_params)
        cursor = conn.cursor()
        
        try:
            # 检查表是否存在
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = %s
                )
            """, (table_name,))
            
            table_exists = cursor.fetchone()[0]
            
            if not table_exists:
                columns = []
                
                # 添加系统字段
                for sys_field in self.system_fields:
                    col_def = self._get_column_sql_def(sys_field['name'], sys_field)
                    if col_def:
                        columns.append(col_def)
                
                # 添加数据字段
                for field_config in field_configs:
                    col_name = field_config.get('target_field')
                    if col_name and col_name not in [c.split()[0] for c in columns]:
                        col_def = self._get_column_sql_def(col_name, field_config)
                        if col_def:
                            columns.append(col_def)
                
                # 添加字典关联字段
                for dict_field in dict_fields:
                    base_name = dict_field['target_field']
                    
                    # {字段}_id - 关联字典表的系统自增id
                    id_col = f"{base_name}_id INTEGER"
                    if id_col not in columns:
                        columns.append(id_col)
                    
                    # {字段}_name - 冗余存储字典表name（方便显示）
                    name_col = f"{base_name}_name VARCHAR(50)"
                    if name_col not in columns:
                        columns.append(name_col)
                    
                    # {字段}_code - 存储原始code值
                    code_col = f"{base_name}_code VARCHAR(30)"
                    if code_col not in columns:
                        columns.append(code_col)
                
                # 创建表
                create_sql = f"CREATE TABLE {table_name} ("
                create_sql += ", ".join(columns)
                create_sql += ")"
                
                cursor.execute(create_sql)
                conn.commit()
                print(f"创建子表: {table_name}")
        finally:
            cursor.close()
            conn.close()
    
    def _process_child_data(self, data: List[Dict], field_configs: List[Dict], 
                           dict_fields: List[Dict]) -> List[Dict]:
        """处理子表数据（关联主表和字典表）"""
        import psycopg2
        
        db_url = self.engine.url
        conn_params = {
            'host': db_url.host,
            'database': db_url.database,
            'user': db_url.username,
            'password': db_url.password,
            'port': db_url.port or 5432
        }
        
        conn = psycopg2.connect(**conn_params)
        cursor = conn.cursor()
        
        processed = []
        
        try:
            # 获取主表id映射（身份证号码 -> id）
            cursor.execute("SELECT id, 身份证号码 FROM teacher_basic")
            id_card_map = {row[1]: row[0] for row in cursor.fetchall()}
            print(f"主表映射: {len(id_card_map)} 条")
            
            # 获取字典表映射（所有字典表都有标准结构：id, code, name）
            dict_maps = {}
            for dict_field in dict_fields:
                dict_table = dict_field['dictionary_table']
                display_field = dict_field.get('dictionary_display_field', 'name')
                if dict_table and dict_table not in dict_maps:
                    # 标准字典表结构：id, code, name
                    cursor.execute(f"SELECT id, code, {display_field} FROM {dict_table}")
                    rows = cursor.fetchall()
                    dict_maps[dict_table] = {
                        'by_code': {str(row[1]): {'id': row[0], 'name': row[2]} for row in rows}
                    }
            
            # 处理每一行数据
            for row in data:
                new_row = {}
                
                # 复制原始字段
                for field_config in field_configs:
                    source_field = field_config['source_field']
                    target_field = field_config['target_field']
                    value = row.get(source_field)
                    
                    # 转换日期格式
                    if field_config.get('data_type') == 'DATE' and value is not None:
                        value = self._convert_date_format(str(value))
                    
                    if value is not None:
                        new_row[target_field] = value
                
                # 关联主表（通过身份证号码）
                id_card = row.get('身份证号码') or row.get('身份证号')
                if id_card:
                    teacher_id = id_card_map.get(str(id_card).strip())
                    if teacher_id:
                        new_row['teacher_id'] = teacher_id
                
                # 关联字典表
                for dict_field in dict_fields:
                    source_field = dict_field['source_field']
                    target_field = dict_field['target_field']
                    dict_table = dict_field['dictionary_table']
                    value_mapping = dict_field.get('value_mapping', {})
                    
                    code_value = row.get(source_field)
                    if code_value is not None and dict_table in dict_maps:
                        code_str = str(code_value).strip()
                        
                        # 应用值映射（如 "1" -> "干部"）
                        if value_mapping and code_str in value_mapping:
                            code_str = value_mapping[code_str]
                        
                        dict_info = dict_maps[dict_table]['by_code'].get(code_str)
                        
                        if dict_info:
                            # 使用字典表的系统自增id作为关联键
                            new_row[f"{target_field}_id"] = dict_info['id']
                            new_row[f"{target_field}_name"] = dict_info['name']
                            new_row[f"{target_field}_code"] = code_str
                
                processed.append(new_row)
        finally:
            cursor.close()
            conn.close()
        
        return processed
    
    def _insert_child_data(self, table_name: str, data: List[Dict]) -> int:
        """插入子表数据"""
        import psycopg2
        
        db_url = self.engine.url
        conn_params = {
            'host': db_url.host,
            'database': db_url.database,
            'user': db_url.username,
            'password': db_url.password,
            'port': db_url.port or 5432
        }
        
        inserted_count = 0
        conn = psycopg2.connect(**conn_params)
        cursor = conn.cursor()
        
        try:
            for row in data:
                if not row:
                    continue
                
                columns = list(row.keys())
                placeholders = ['%s'] * len(columns)
                values = [row[col] for col in columns]
                
                insert_sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"
                
                try:
                    cursor.execute(insert_sql, values)
                    inserted_count += 1
                except Exception as e:
                    print(f"插入失败: {e}, 数据: {row}")
            
            conn.commit()
        finally:
            cursor.close()
            conn.close()
        
        return inserted_count
    
    def _get_column_sql_def(self, col_name: str, field_config: Dict) -> Optional[str]:
        """生成列的SQL定义字符串"""
        data_type = field_config.get('data_type', 'VARCHAR')
        
        # 处理系统字段
        if col_name == 'id' and field_config.get('primary_key'):
            return f"{col_name} SERIAL PRIMARY KEY"
        
        if data_type == 'INTEGER':
            return f"{col_name} INTEGER"
        elif data_type == 'DECIMAL':
            precision = field_config.get('precision', 10)
            scale = field_config.get('scale', 2)
            return f"{col_name} NUMERIC({precision}, {scale})"
        elif data_type == 'DATE':
            return f"{col_name} DATE"
        elif data_type == 'DATETIME' or data_type == 'TIMESTAMP':
            default = field_config.get('default', '')
            if 'CURRENT_TIMESTAMP' in str(default):
                return f"{col_name} TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
            return f"{col_name} TIMESTAMP"
        elif data_type == 'BOOLEAN':
            default = field_config.get('default', '')
            if default == True or default == 'true':
                return f"{col_name} BOOLEAN DEFAULT true"
            return f"{col_name} BOOLEAN"
        elif data_type == 'TEXT':
            return f"{col_name} TEXT"
        else:  # VARCHAR
            length = field_config.get('length', 255)
            return f"{col_name} VARCHAR({length})"
    
    def _convert_date_format(self, value: str) -> str:
        """转换日期格式"""
        if not value or pd.isna(value):
            return None
        
        value_str = str(value).strip()
        if not value_str:
            return None
        
        # 如果已经是标准格式，直接返回
        if re.match(r'^\d{4}-\d{2}-\d{2}$', value_str):
            return value_str
        
        # 获取配置的输入格式
        date_formats = self.config.get('date_formats', {})
        input_formats = date_formats.get('input_formats', [
            '%Y-%m-%d', '%Y/%m/%d', '%Y年%m月%d日'
        ])
        
        # 尝试解析各种格式
        for fmt in input_formats:
            try:
                dt = datetime.strptime(value_str, fmt)
                return dt.strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        # 特殊处理：2001-1-1, 2001/1/1 等格式
        if re.match(r'^\d{4}-\d{1,2}-\d{1,2}$', value_str):
            year, month, day = value_str.split('-')
            return f"{year}-{int(month):02d}-{int(day):02d}"
        
        if re.match(r'^\d{4}/\d{1,2}/\d{1,2}$', value_str):
            year, month, day = value_str.split('/')
            return f"{year}-{int(month):02d}-{int(day):02d}"
        
        if re.match(r'^\d{4}年\d{1,2}月\d{1,2}日$', value_str):
            match = re.match(r'^(\d{4})年(\d{1,2})月(\d{1,2})日$', value_str)
            if match:
                year, month, day = match.groups()
                return f"{year}-{int(month):02d}-{int(day):02d}"
        
        return value_str


if __name__ == "__main__":
    # 测试代码
    service = UniversalImportServiceV2()
    print("通用导入服务 V2 初始化成功")
