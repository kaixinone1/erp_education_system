#!/usr/bin/env python3
"""
通用导入服务 - 配置化、可扩展的导入功能
"""

import json
import os
import re
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from sqlalchemy import create_engine, Table, Column, MetaData, String, Integer, Float, Date, DateTime, Boolean, Text, Numeric
from sqlalchemy.sql import text


class UniversalImportService:
    """
    通用导入服务
    
    特性：
    1. 配置化字段映射 - 通过配置文件定义字段映射规则
    2. 智能数据类型推断 - 自动识别数据类型
    3. 自动日期格式转换 - 支持多种日期格式
    4. 通用验证规则引擎 - 通过配置定义验证规则
    5. 灵活的外键关联 - 支持多种关联方式
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
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """加载配置文件"""
        default_config = {
            "field_type_mappings": {"rules": []},
            "validation_rules": {},
            "date_formats": {"auto_convert": True},
            "system_fields": {"fields": []}
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
    
    def analyze_file(self, file_path: str or bytes, file_name: str) -> Dict[str, Any]:
        """
        分析文件，生成字段映射建议
        
        Returns:
            {
                "fields": [字段名列表],
                "preview_data": [预览数据],
                "suggested_mappings": [字段映射建议],
                "total_rows": 总行数
            }
        """
        # 读取文件
        if isinstance(file_path, str):
            if file_name.endswith('.csv'):
                df = pd.read_csv(file_path, encoding='utf-8')
            else:
                df = pd.read_excel(file_path)
        else:
            # bytes
            if file_name.endswith('.csv'):
                df = pd.read_csv(pd.io.common.BytesIO(file_path), encoding='utf-8')
            else:
                df = pd.read_excel(pd.io.common.BytesIO(file_path))
        
        original_fields = df.columns.tolist()
        
        # 生成字段映射建议
        suggested_mappings = []
        for field in original_fields:
            mapping = self._generate_field_mapping(field, df[field].tolist())
            suggested_mappings.append(mapping)
        
        # 获取预览数据（前10行）
        preview_data = df.head(10).to_dict(orient='records')
        
        # 转换日期格式
        date_fields = [m['source_field'] for m in suggested_mappings 
                      if m.get('data_type') == 'DATE']
        
        for row in preview_data:
            for key, value in row.items():
                if pd.isna(value):
                    row[key] = None
                elif key in date_fields and value is not None:
                    row[key] = self._convert_date_format(str(value))
        
        return {
            "fields": original_fields,
            "preview_data": preview_data,
            "suggested_mappings": suggested_mappings,
            "total_rows": len(df)
        }
    
    def _generate_field_mapping(self, field_name: str, values: List[Any]) -> Dict[str, Any]:
        """
        生成字段映射建议
        
        1. 首先匹配配置规则
        2. 然后推断数据类型
        """
        # 尝试匹配配置规则
        mapping_rules = self.config.get('field_type_mappings', {}).get('rules', [])
        
        for rule in mapping_rules:
            pattern = rule.get('pattern', '')
            if re.search(pattern, field_name):
                return {
                    "source_field": field_name,
                    "target_field": rule.get('target_field', field_name),
                    "data_type": rule.get('data_type', 'VARCHAR'),
                    "length": rule.get('length', 255),
                    "confidence": "high",
                    "relation_type": "none",
                    "relation_table": "",
                    "relation_display_field": ""
                }
        
        # 如果没有匹配到规则，推断数据类型
        inferred = self._infer_data_type(values)
        
        # 生成目标字段名
        target_field = self._generate_target_field_name(field_name)
        
        return {
            "source_field": field_name,
            "target_field": target_field,
            "data_type": inferred.get('data_type', 'VARCHAR'),
            "length": inferred.get('length', 255),
            "confidence": "low",
            "relation_type": "none",
            "relation_table": "",
            "relation_display_field": ""
        }
    
    def _infer_data_type(self, values: List[Any]) -> Dict[str, Any]:
        """推断数据类型"""
        # 过滤空值
        non_null_values = [str(v) for v in values if pd.notna(v) and str(v).strip()]
        
        if not non_null_values:
            return {"data_type": "VARCHAR", "length": 255}
        
        # 获取推断规则
        inference_rules = self.config.get('data_type_inference', {}).get('rules', [])
        
        for rule in inference_rules:
            data_type = rule.get('data_type', '')
            patterns = rule.get('patterns', [])
            
            match_count = 0
            for value in non_null_values:
                for pattern in patterns:
                    if re.match(pattern, str(value), re.IGNORECASE):
                        match_count += 1
                        break
            
            # 如果80%以上的数据匹配该类型，则使用该类型
            if match_count / len(non_null_values) >= 0.8:
                if data_type == "INTEGER":
                    return {"data_type": "INTEGER"}
                elif data_type == "DECIMAL":
                    return {"data_type": "DECIMAL", "precision": 10, "scale": 2}
                elif data_type == "DATE":
                    return {"data_type": "DATE"}
                elif data_type == "BOOLEAN":
                    return {"data_type": "BOOLEAN"}
        
        # 默认为VARCHAR，根据内容长度确定
        max_length = max(len(str(v)) for v in non_null_values)
        # 向上取整到标准长度
        standard_lengths = [10, 20, 50, 100, 200, 500, 1000]
        length = next((l for l in standard_lengths if max_length <= l), 2000)
        
        return {"data_type": "VARCHAR", "length": length}
    
    def _generate_target_field_name(self, source_field: str) -> str:
        """生成目标字段名"""
        # 清理字段名
        clean_field = re.sub(r'[^\w\s]', '', source_field)
        clean_field = re.sub(r'\s+', '_', clean_field).lower()
        
        # 如果转换后为空，使用默认名称
        if not clean_field:
            clean_field = f"field_{hash(source_field) % 10000}"
        
        return clean_field
    
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
    
    def validate_data(self, data: List[Dict], field_configs: List[Dict]) -> Dict[str, Any]:
        """
        验证数据
        
        Returns:
            {
                "valid": True/False,
                "errors": [],
                "warnings": []
            }
        """
        errors = []
        warnings = []
        
        # 获取验证规则
        validation_rules = self.config.get('validation_rules', {})
        
        for row_idx, row in enumerate(data):
            for field_config in field_configs:
                source_field = field_config.get('source_field')
                target_field = field_config.get('target_field')
                data_type = field_config.get('data_type')
                
                value = row.get(source_field)
                
                if value is None or pd.isna(value):
                    continue
                
                value_str = str(value).strip()
                
                # 根据数据类型验证
                if target_field in validation_rules:
                    rule = validation_rules[target_field]
                    pattern = rule.get('pattern', '')
                    if pattern and not re.match(pattern, value_str):
                        errors.append({
                            "row": row_idx + 1,
                            "field": source_field,
                            "message": rule.get('message', f'{source_field}格式不正确')
                        })
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    def import_data(self, 
                   table_name: str,
                   field_configs: List[Dict],
                   data: List[Dict],
                   table_type: str = "master",
                   parent_table: str = None) -> Dict[str, Any]:
        """
        导入数据
        
        Args:
            table_name: 目标表名
            field_configs: 字段配置
            data: 要导入的数据
            table_type: 表类型 (master/child/dictionary)
            parent_table: 父表名（子表使用）
        
        Returns:
            {
                "success": True/False,
                "inserted": 插入条数,
                "updated": 更新条数,
                "errors": 错误信息
            }
        """
        try:
            # 1. 创建或更新表结构
            self._create_or_update_table(table_name, field_configs, table_type)
            
            # 2. 处理数据
            processed_data = self._process_data(data, field_configs)
            
            # 3. 插入数据
            inserted_count = self._insert_data(table_name, processed_data, field_configs)
            
            return {
                "success": True,
                "inserted": inserted_count,
                "updated": 0,
                "errors": []
            }
            
        except Exception as e:
            return {
                "success": False,
                "inserted": 0,
                "updated": 0,
                "errors": [str(e)]
            }
    
    def _create_or_update_table(self, table_name: str, field_configs: List[Dict], table_type: str):
        """创建或更新表结构"""
        import psycopg2
        
        # 解析数据库连接URL
        db_url = self.engine.url
        conn_params = {
            'host': db_url.host,
            'database': db_url.database,
            'user': db_url.username,
            'password': db_url.password,
            'port': db_url.port or 5432
        }
        
        # 构建列定义
        columns = []
        
        # 添加系统字段
        if self.config.get('system_fields', {}).get('auto_add', True):
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
        
        # 创建表
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
                # 创建新表
                create_sql = f"CREATE TABLE {table_name} ("
                create_sql += ", ".join(columns)
                create_sql += ")"
                
                cursor.execute(create_sql)
                conn.commit()
                print(f"创建表: {table_name}")
        finally:
            cursor.close()
            conn.close()
    
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
            return f"{col_name} BOOLEAN"
        elif data_type == 'TEXT':
            return f"{col_name} TEXT"
        else:  # VARCHAR
            length = field_config.get('length', 255)
            return f"{col_name} VARCHAR({length})"
    
    def _create_column(self, col_name: str, field_config: Dict) -> Optional[Column]:
        """创建列定义（SQLAlchemy Column对象）"""
        data_type = field_config.get('data_type', 'VARCHAR')
        
        if data_type == 'INTEGER':
            return Column(col_name, Integer)
        elif data_type == 'DECIMAL':
            precision = field_config.get('precision', 10)
            scale = field_config.get('scale', 2)
            return Column(col_name, Numeric(precision, scale))
        elif data_type == 'DATE':
            return Column(col_name, Date)
        elif data_type == 'DATETIME':
            return Column(col_name, DateTime)
        elif data_type == 'BOOLEAN':
            return Column(col_name, Boolean)
        elif data_type == 'TEXT':
            return Column(col_name, Text)
        else:  # VARCHAR
            length = field_config.get('length', 255)
            return Column(col_name, String(length))
    
    def _get_column_type(self, column: Column) -> str:
        """获取列的SQL类型定义"""
        if isinstance(column.type, Integer):
            return "INTEGER"
        elif isinstance(column.type, Numeric):
            return f"NUMERIC({column.type.precision}, {column.type.scale})"
        elif isinstance(column.type, Date):
            return "DATE"
        elif isinstance(column.type, DateTime):
            return "TIMESTAMP"
        elif isinstance(column.type, Boolean):
            return "BOOLEAN"
        elif isinstance(column.type, Text):
            return "TEXT"
        elif isinstance(column.type, String):
            return f"VARCHAR({column.type.length})"
        else:
            return "VARCHAR(255)"
    
    def _process_data(self, data: List[Dict], field_configs: List[Dict]) -> List[Dict]:
        """处理数据"""
        field_mapping = {f['source_field']: f for f in field_configs}
        
        processed = []
        for row in data:
            new_row = {}
            for source_field, value in row.items():
                if source_field in field_mapping:
                    field_config = field_mapping[source_field]
                    target_field = field_config.get('target_field')
                    data_type = field_config.get('data_type')
                    
                    # 转换日期格式
                    if data_type == 'DATE' and value is not None:
                        value = self._convert_date_format(str(value))
                    
                    if value is not None:
                        new_row[target_field] = value
            
            processed.append(new_row)
        
        return processed
    
    def _insert_data(self, table_name: str, data: List[Dict], field_configs: List[Dict]) -> int:
        """插入数据"""
        if not data:
            return 0
        
        import psycopg2
        
        # 解析数据库连接URL
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
