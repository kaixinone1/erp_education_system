#!/usr/bin/env python3
"""
通用导入服务 V3 - 100% 配置驱动

核心原则：
1. 所有行为由配置文件决定
2. 动态生成 SQL，不预先编写特定表的 SQL
3. 统一的四步导入流程
4. 强化验证引擎
"""

import json
import os
import re
import psycopg2
from psycopg2 import pool
from typing import List, Dict, Any, Optional, Tuple, Set
from datetime import datetime
from contextlib import contextmanager


class UniversalImportServiceV3:
    """
    通用导入服务 - 配置驱动
    """
    
    def __init__(self, db_params: Dict[str, str] = None):
        if db_params is None:
            db_params = {
                'host': 'localhost',
                'database': 'taiping_education',
                'user': 'taiping_user',
                'password': 'taiping_password'
            }
        
        self.db_params = db_params
        self.connection_pool = psycopg2.pool.SimpleConnectionPool(1, 10, **db_params)
        
        # 加载配置
        self.config = self._load_config()
        
        # 缓存
        self._master_cache = None
        self._dict_cache = {}
    
    def _load_config(self) -> Dict:
        """加载导入配置"""
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'config', 'import_config_v2.json'
        )
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载配置失败: {e}")
            return {}
    
    @contextmanager
    def get_connection(self):
        """获取数据库连接"""
        conn = self.connection_pool.getconn()
        try:
            yield conn
        finally:
            self.connection_pool.putconn(conn)
    
    def import_data(self, table_name: str, field_configs: List[Dict], 
                    data: List[Dict], chinese_table_name: str = "",
                    auto_manage_dict: bool = False) -> Dict[str, Any]:
        """
        导入数据 - 主入口
        
        Args:
            table_name: 英文表名
            field_configs: 字段配置列表（用户确认的）
            data: 要导入的数据
            chinese_table_name: 中文表名
            auto_manage_dict: 自动管理字典表（兼容旧接口，暂未使用）
        
        Returns:
            {"success": True/False, "inserted": 数量, "errors": []}
        """
        try:
            print(f"\n{'='*80}")
            print(f"开始导入数据到表: {table_name}")
            print(f"数据条数: {len(data)}")
            print(f"字段配置数: {len(field_configs)}")
            print(f"{'='*80}")
            
            if not data:
                return {"success": False, "inserted": 0, "errors": ["数据为空"]}
            
            if not field_configs:
                return {"success": False, "inserted": 0, "errors": ["字段配置为空"]}
            
            # 1. 根据配置创建/更新表结构
            self._create_or_update_table(table_name, field_configs)
            
            # 2. 处理数据（根据配置进行转换和验证）
            processed_data = self._process_data(data, field_configs)
            
            # 3. 批量插入数据
            inserted_count = self._batch_insert(table_name, processed_data, field_configs)
            
            print(f"\n{'='*80}")
            print(f"导入完成！成功插入 {inserted_count} 条记录")
            print(f"{'='*80}")
            
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
    
    def _create_or_update_table(self, table_name: str, field_configs: List[Dict]):
        """根据字段配置创建或更新表结构"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 检查表是否存在
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = %s
                )
            """, (table_name,))
            table_exists = cursor.fetchone()[0]
            
            if table_exists:
                # 表存在，检查是否需要添加新列
                self._update_table_columns(cursor, table_name, field_configs)
            else:
                # 表不存在，创建新表
                self._create_table(cursor, table_name, field_configs)
            
            conn.commit()
            cursor.close()
    
    def _create_table(self, cursor, table_name: str, field_configs: List[Dict]):
        """创建新表"""
        columns = ["id SERIAL PRIMARY KEY"]
        
        # 添加用户配置的字段
        for field in field_configs:
            col_def = self._build_column_definition(field)
            if col_def:
                columns.append(col_def)
        
        # 添加系统字段
        system_fields = self.config.get('system_fields', {}).get('fields', [])
        for sys_field in system_fields:
            if sys_field['name'] != 'id':  # id 已经添加
                col_def = self._build_system_column_definition(sys_field)
                if col_def:
                    columns.append(col_def)
        
        create_sql = f"CREATE TABLE {table_name} ({', '.join(columns)})"
        print(f"  创建表: {table_name}")
        print(f"  SQL: {create_sql}")
        cursor.execute(create_sql)
    
    def _update_table_columns(self, cursor, table_name: str, field_configs: List[Dict]):
        """更新表结构（添加新列）"""
        # 获取现有列
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = %s
        """, (table_name,))
        existing_columns = {row[0] for row in cursor.fetchall()}
        
        # 检查需要添加的新列
        for field in field_configs:
            target_field = field.get('target_field') or field.get('english_name')
            if target_field and target_field not in existing_columns:
                col_def = self._build_column_definition(field)
                if col_def:
                    alter_sql = f"ALTER TABLE {table_name} ADD COLUMN {col_def}"
                    print(f"  添加列: {target_field}")
                    cursor.execute(alter_sql)
    
    def _build_column_definition(self, field: Dict) -> Optional[str]:
        """构建列定义"""
        target = field.get('target_field') or field.get('english_name')
        if not target:
            return None
        
        data_type = field.get('data_type', 'VARCHAR')
        length = field.get('length', 255)
        
        # 构建数据类型
        if data_type == 'VARCHAR':
            type_str = f"VARCHAR({length})"
        elif data_type == 'DECIMAL':
            precision = field.get('precision', 10)
            scale = field.get('scale', 2)
            type_str = f"DECIMAL({precision}, {scale})"
        else:
            type_str = data_type
        
        # 构建约束
        constraints = []
        if field.get('required') or field.get('not_null'):
            constraints.append("NOT NULL")
        if field.get('unique'):
            constraints.append("UNIQUE")
        if field.get('default_value'):
            constraints.append(f"DEFAULT {field['default_value']}")
        
        return f"{target} {type_str} {' '.join(constraints)}".strip()
    
    def _build_system_column_definition(self, field: Dict) -> Optional[str]:
        """构建系统列定义"""
        name = field['name']
        data_type = field['data_type']
        default = field.get('default', '')
        
        if default:
            return f"{name} {data_type} DEFAULT {default}"
        return f"{name} {data_type}"
    
    def _process_data(self, data: List[Dict], field_configs: List[Dict]) -> List[Dict]:
        """处理数据 - 根据配置进行转换"""
        processed = []
        
        # 构建字段映射
        field_mapping = {}
        for field in field_configs:
            source = field.get('source_field') or field.get('chinese_name')
            target = field.get('target_field') or field.get('english_name')
            if source and target:
                field_mapping[source] = {
                    'target': target,
                    'data_type': field.get('data_type', 'VARCHAR'),
                    'field_config': field
                }
        
        print(f"  字段映射: {field_mapping}")
        
        for row in data:
            new_row = {}
            
            for source_field, mapping_info in field_mapping.items():
                value = row.get(source_field)
                target = mapping_info['target']
                data_type = mapping_info['data_type']
                
                # 转换数据类型
                if value is not None:
                    converted_value = self._convert_value(value, data_type)
                    if converted_value is not None:
                        new_row[target] = converted_value
            
            processed.append(new_row)
        
        print(f"  处理后的数据条数: {len(processed)}")
        return processed
    
    def _convert_value(self, value: Any, data_type: str) -> Any:
        """转换数据类型"""
        if value is None or value == '':
            return None
        
        try:
            if data_type == 'INTEGER':
                return int(value)
            elif data_type == 'DECIMAL' or data_type == 'NUMERIC':
                return float(value)
            elif data_type == 'BOOLEAN':
                return str(value).lower() in ('true', '1', '是', 'yes')
            elif data_type == 'DATE':
                # 日期格式转换
                return self._convert_date(str(value))
            else:
                return str(value)
        except Exception as e:
            print(f"  转换失败: {value} -> {data_type}, 错误: {e}")
            return None
    
    def _convert_date(self, value: str) -> Optional[str]:
        """转换日期格式"""
        date_formats = self.config.get('date_formats', {}).get('input_formats', [])
        
        for fmt in date_formats:
            try:
                from datetime import datetime
                dt = datetime.strptime(value, fmt)
                return dt.strftime('%Y-%m-%d')
            except:
                continue
        
        return value  # 如果都失败，返回原值
    
    def _batch_insert(self, table_name: str, data: List[Dict], field_configs: List[Dict]) -> int:
        """批量插入数据"""
        if not data:
            print("  警告: 没有数据需要插入")
            return 0
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 获取列名（从第一条数据）
            columns = list(data[0].keys())
            
            if not columns:
                print("  警告: 没有列需要插入")
                return 0
            
            column_str = ', '.join(columns)
            placeholders = ', '.join(['%s'] * len(columns))
            
            insert_sql = f"INSERT INTO {table_name} ({column_str}) VALUES ({placeholders})"
            
            # 准备数据
            values = []
            for row in data:
                row_values = []
                for col in columns:
                    row_values.append(row.get(col))
                values.append(tuple(row_values))
            
            print(f"  插入SQL: {insert_sql}")
            print(f"  数据条数: {len(values)}")
            print(f"  示例数据: {values[0] if values else 'None'}")
            
            try:
                cursor.executemany(insert_sql, values)
                conn.commit()
                inserted = cursor.rowcount
                cursor.close()
                return inserted
            except Exception as e:
                conn.rollback()
                cursor.close()
                print(f"  插入失败: {e}")
                raise
    
    def close(self):
        """关闭连接池"""
        if self.connection_pool:
            self.connection_pool.closeall()
