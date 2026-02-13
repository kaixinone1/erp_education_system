#!/usr/bin/env python3
"""
通用导入服务 - 100% 配置驱动

核心原则：
1. 所有行为由配置文件决定
2. 动态生成 SQL，不预先编写特定表的 SQL
3. 原子化导入事务
4. 无硬编码字段名或表名
"""

from typing import List, Dict, Any, Optional
import json
import os
import re
import uuid
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool


class ImportService:
    """
    通用导入服务 - 配置驱动
    """
    
    def __init__(self, db_url: str = None):
        # 数据库连接
        if db_url is None:
            db_url = "postgresql://taiping_user:taiping_password@localhost:5432/taiping_education"
        self.engine = create_engine(db_url, poolclass=NullPool)
        
        # 配置文件路径
        self.config_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config')
        self.navigation_file = os.path.join(self.config_dir, 'navigation.json')
        self.schema_file = os.path.join(self.config_dir, 'merged_schema_mappings.json')
        self.table_schemas_file = os.path.join(self.config_dir, 'table_schemas.json')
        
        # 加载配置
        self.config = self._load_config()
    
    def _load_config(self) -> Dict:
        """加载配置文件"""
        try:
            with open(self.schema_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载配置失败: {e}")
            return {"tables": {}, "mappings": {}, "validation_rules": {}}
    
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
        原子化导入数据
        
        Args:
            table_name: 目标表名（英文）
            field_configs: 字段配置列表
            data: 要导入的数据
            module_id: 归属模块ID
            module_name: 归属模块名称
            table_type: 表类型 (master/child/dictionary)
            parent_table: 父表名（子表使用）
            foreign_keys: 外键配置列表
            file_name: 原始文件名
            chinese_title: 中文标题
            sub_module_id: 子模块ID
            sub_module_name: 子模块名称
        
        Returns:
            导入结果
        """
        try:
            print(f"\n{'='*80}")
            print(f"开始导入数据")
            print(f"表名: {table_name}")
            print(f"中文标题: {chinese_title}")
            print(f"表类型: {table_type}")
            print(f"数据条数: {len(data)}")
            print(f"{'='*80}")
            
            if not data:
                return {"status": "error", "message": "数据为空", "record_count": 0}
            
            if not field_configs:
                return {"status": "error", "message": "字段配置为空", "record_count": 0}
            
            # 步骤1: 动态建表
            actual_table_name, is_existing_table = self._create_or_update_table(
                table_name=table_name,
                field_configs=field_configs,
                table_type=table_type,
                parent_table=parent_table,
                foreign_keys=foreign_keys
            )
            
            # 步骤2: 插入数据
            if is_existing_table:
                inserted_count, updated_count, errors = self._upsert_data(
                    table_name=actual_table_name,
                    field_configs=field_configs,
                    data=data
                )
                total_count = inserted_count + updated_count
                message = f"成功导入 {total_count} 条数据（新增 {inserted_count} 条，更新 {updated_count} 条）"
            else:
                inserted_count, errors = self._insert_data(
                    table_name=actual_table_name,
                    field_configs=field_configs,
                    data=data
                )
                total_count = inserted_count
                message = f"成功导入 {inserted_count} 条数据"
            
            # 步骤3: 更新配置文件
            self._update_schema_config(
                table_name=actual_table_name,
                chinese_title=chinese_title,
                field_configs=field_configs,
                table_type=table_type,
                parent_table=parent_table
            )
            
            # 步骤4: 更新导航
            print(f"\n{'='*80}")
            print(f"步骤4: 更新导航配置")
            print(f"module_id: {module_id}")
            print(f"module_name: {module_name}")
            print(f"chinese_title: {chinese_title}")
            print(f"{'='*80}")
            
            try:
                self._update_navigation_config(
                    table_name=actual_table_name,
                    chinese_title=chinese_title,
                    module_id=module_id,
                    module_name=module_name,
                    table_type=table_type,
                    parent_table=parent_table,
                    sub_module_id=sub_module_id,
                    sub_module_name=sub_module_name
                )
                print("导航配置更新成功")
            except Exception as nav_error:
                print(f"导航配置更新失败: {nav_error}")
                import traceback
                traceback.print_exc()
            
            result = {
                "status": "success" if not errors else "partial_success",
                "message": message,
                "table_name": actual_table_name,
                "chinese_name": chinese_title,
                "table_type": table_type,
                "record_count": total_count,
                "inserted": inserted_count,
                "updated": updated_count if is_existing_table else 0,
                "is_existing_table": is_existing_table
            }
            
            if errors:
                result["errors"] = errors
            
            print(f"\n{'='*80}")
            print(f"导入完成: {message}")
            print(f"{'='*80}")
            
            return result
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            raise Exception(f"导入失败: {str(e)}")
    
    def _create_or_update_table(self, 
                               table_name: str, 
                               field_configs: List[Dict[str, Any]],
                               table_type: str = "master",
                               parent_table: Optional[str] = None,
                               foreign_keys: Optional[List[Dict[str, Any]]] = None) -> tuple:
        """
        动态创建或更新数据表
        返回: (实际使用的表名, 是否是已存在的表)
        """
        # 检查表是否已存在
        if self._table_exists(table_name):
            print(f"表 {table_name} 已存在，使用现有表")
            return table_name, True
        
        # 检查是否存在结构相同的表
        existing_table = self._find_matching_table(field_configs)
        if existing_table:
            print(f"找到匹配的表: {existing_table}，使用现有表")
            return existing_table, True
        
        # 创建新表
        self._create_table(table_name, field_configs, table_type, foreign_keys)
        return table_name, False
    
    def _table_exists(self, table_name: str) -> bool:
        """检查表是否存在"""
        with self.engine.connect() as conn:
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = :table_name AND table_schema = 'public'
                )
            """), {"table_name": table_name})
            return result.scalar()
    
    def _find_matching_table(self, field_configs: List[Dict]) -> Optional[str]:
        """查找是否存在字段结构匹配的现有表"""
        new_signature = self._get_table_signature(field_configs)
        
        with self.engine.connect() as conn:
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """))
            db_tables = [row[0] for row in result]
        
        for table_name in db_tables:
            existing_signature = self._get_table_signature_from_db(table_name)
            if existing_signature and self._compare_signatures(new_signature, existing_signature):
                return table_name
        
        return None
    
    def _get_table_signature(self, field_configs: List[Dict]) -> List[tuple]:
        """获取表的字段签名"""
        signature = []
        for field in field_configs:
            target = field.get('targetField') or field.get('english_name', '')
            data_type = field.get('dataType') or field.get('data_type', 'VARCHAR')
            if target:
                signature.append((target.lower(), data_type.lower()))
        return sorted(signature)
    
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
                    if col_name in ['id', 'created_at', 'updated_at']:
                        continue
                    signature.append((col_name.lower(), data_type.lower()))
                return signature
        except Exception as e:
            print(f"获取表签名失败: {e}")
            return None
    
    def _compare_signatures(self, sig1: List[tuple], sig2: List[tuple]) -> bool:
        """比较两个表签名是否匹配"""
        if len(sig1) != len(sig2):
            return False
        
        # 标准化数据类型后比较
        normalized_sig1 = [(name, self._normalize_data_type(t)) for name, t in sig1]
        normalized_sig2 = [(name, self._normalize_data_type(t)) for name, t in sig2]
        
        return normalized_sig1 == normalized_sig2
    
    def _normalize_data_type(self, data_type: str) -> str:
        """标准化数据类型"""
        dt = data_type.lower()
        if dt in ['integer', 'int', 'int4']:
            return 'integer'
        elif dt in ['varchar', 'character varying', 'text']:
            return 'varchar'
        elif dt in ['decimal', 'numeric']:
            return 'decimal'
        elif dt in ['date']:
            return 'date'
        elif dt in ['timestamp', 'datetime', 'timestamp without time zone']:
            return 'timestamp'
        elif dt in ['boolean', 'bool']:
            return 'boolean'
        return dt
    
    def _create_table(self, table_name: str, field_configs: List[Dict], 
                     table_type: str, foreign_keys: Optional[List[Dict]] = None):
        """创建新表"""
        columns = ["id SERIAL PRIMARY KEY"]
        
        # 添加用户配置的字段
        for field in field_configs:
            col_def = self._build_column_definition(field)
            if col_def:
                columns.append(col_def)
        
        # 添加系统字段
        columns.extend([
            "created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
            "updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
        ])
        
        # 添加外键约束
        if foreign_keys:
            for fk in foreign_keys:
                ref_table = fk.get('ref_table')
                ref_field = fk.get('ref_field')
                local_field = fk.get('local_field')
                if ref_table and ref_field and local_field:
                    columns.append(f"FOREIGN KEY ({local_field}) REFERENCES {ref_table}({ref_field})")
        
        create_sql = f"CREATE TABLE {table_name} ({', '.join(columns)})"
        print(f"创建表 SQL: {create_sql}")
        
        with self.engine.connect() as conn:
            conn.execute(text(create_sql))
            conn.commit()
    
    def _build_column_definition(self, field: Dict) -> Optional[str]:
        """构建列定义"""
        target = field.get('targetField') or field.get('english_name')
        if not target:
            return None
        
        data_type = field.get('dataType') or field.get('data_type', 'VARCHAR')
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
        
        return f"{target} {type_str} {' '.join(constraints)}".strip()
    
    def _insert_data(self, table_name: str, field_configs: List[Dict], 
                    data: List[Dict]) -> tuple:
        """批量插入数据"""
        if not data:
            return 0, []
        
        # 构建字段映射
        field_mapping = {}
        for field in field_configs:
            source = field.get('sourceField') or field.get('chinese_name', '')
            target = field.get('targetField') or field.get('english_name', '')
            if source and target:
                field_mapping[source] = target
        
        print(f"字段映射: {field_mapping}")
        print(f"准备批量插入 {len(data)} 条数据...")
        
        # 准备批量插入数据
        batch_data = []
        errors = []
        
        for row_idx, row in enumerate(data):
            try:
                insert_data = {}
                for source_field, target_field in field_mapping.items():
                    value = row.get(source_field)
                    
                    # 数据清洗和转换
                    if value is not None and str(value).strip() != '':
                        # 日期格式转换
                        if self._is_date_field(target_field, field_configs):
                            value = self._convert_date(value)
                        insert_data[target_field] = value
                
                if insert_data:
                    batch_data.append(insert_data)
                    
            except Exception as e:
                errors.append(f"第 {row_idx + 1} 行数据准备失败: {str(e)}")
        
        if not batch_data:
            return 0, errors
        
        # 批量插入
        inserted_count = 0
        batch_size = 100  # 每批100条
        
        with self.engine.connect() as conn:
            for i in range(0, len(batch_data), batch_size):
                batch = batch_data[i:i + batch_size]
                try:
                    # 获取所有字段
                    all_columns = set()
                    for row in batch:
                        all_columns.update(row.keys())
                    columns = sorted(all_columns)
                    
                    # 构建批量 INSERT 语句
                    values_list = []
                    params = {}
                    for idx, row in enumerate(batch):
                        placeholders = []
                        for col in columns:
                            param_name = f"p{idx}_{col}"
                            placeholders.append(f":{param_name}")
                            params[param_name] = row.get(col)
                        values_list.append(f"({', '.join(placeholders)})")
                    
                    insert_sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES {', '.join(values_list)}"
                    conn.execute(text(insert_sql), params)
                    inserted_count += len(batch)
                    print(f"已插入 {inserted_count}/{len(batch_data)} 条数据...")
                    
                except Exception as e:
                    errors.append(f"批量插入失败 (第 {i+1}-{i+len(batch)} 行): {str(e)}")
            
            conn.commit()
        
        print(f"批量插入完成，共插入 {inserted_count} 条数据")
        return inserted_count, errors
    
    def _upsert_data(self, table_name: str, field_configs: List[Dict], 
                    data: List[Dict]) -> tuple:
        """插入或更新数据"""
        if not data:
            return 0, 0, []
        
        # 构建字段映射
        field_mapping = {}
        for field in field_configs:
            source = field.get('sourceField') or field.get('chinese_name', '')
            target = field.get('targetField') or field.get('english_name', '')
            if source and target:
                field_mapping[source] = target
        
        # 查找唯一键字段
        unique_fields = [f.get('targetField') or f.get('english_name') 
                        for f in field_configs if f.get('unique')]
        
        inserted_count = 0
        updated_count = 0
        errors = []
        
        with self.engine.connect() as conn:
            for row_idx, row in enumerate(data):
                try:
                    insert_data = {}
                    for source_field, target_field in field_mapping.items():
                        value = row.get(source_field)
                        if value is not None and str(value).strip() != '':
                            if self._is_date_field(target_field, field_configs):
                                value = self._convert_date(value)
                            insert_data[target_field] = value
                    
                    if not insert_data:
                        continue
                    
                    # 检查是否存在
                    if unique_fields:
                        where_conditions = []
                        where_values = {}
                        for uf in unique_fields:
                            if uf in insert_data:
                                where_conditions.append(f"{uf} = :{uf}_check")
                                where_values[f"{uf}_check"] = insert_data[uf]
                        
                        if where_conditions:
                            check_sql = f"SELECT id FROM {table_name} WHERE {' AND '.join(where_conditions)} LIMIT 1"
                            result = conn.execute(text(check_sql), where_values)
                            existing = result.fetchone()
                            
                            if existing:
                                # 更新
                                update_sets = [f"{k} = :{k}" for k in insert_data.keys()]
                                update_sql = f"UPDATE {table_name} SET {', '.join(update_sets)} WHERE id = :id"
                                insert_data['id'] = existing[0]
                                conn.execute(text(update_sql), insert_data)
                                updated_count += 1
                                continue
                    
                    # 插入
                    columns = list(insert_data.keys())
                    placeholders = [f":{col}" for col in columns]
                    insert_sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"
                    conn.execute(text(insert_sql), insert_data)
                    inserted_count += 1
                    
                except Exception as e:
                    errors.append(f"第 {row_idx + 1} 行处理失败: {str(e)}")
            
            conn.commit()
        
        return inserted_count, updated_count, errors
    
    def _is_date_field(self, field_name: str, field_configs: List[Dict]) -> bool:
        """检查字段是否为日期类型"""
        for field in field_configs:
            target = field.get('targetField') or field.get('english_name', '')
            if target == field_name:
                data_type = field.get('dataType') or field.get('data_type', '')
                return data_type in ['DATE', 'DATETIME', 'TIMESTAMP']
        return False
    
    def _convert_date(self, value: Any) -> str:
        """转换日期格式"""
        if not value:
            return None
        
        value_str = str(value).strip()
        
        # 如果已经是标准格式，直接返回
        if re.match(r'^\d{4}-\d{2}-\d{2}$', value_str):
            return value_str
        
        # 尝试各种格式
        patterns = [
            (r'^(\d{4})-(\d{1,2})-(\d{1,2})$', lambda m: f"{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"),
            (r'^(\d{4})/(\d{1,2})/(\d{1,2})$', lambda m: f"{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"),
            (r'^(\d{4})年(\d{1,2})月(\d{1,2})日$', lambda m: f"{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"),
        ]
        
        for pattern, formatter in patterns:
            match = re.match(pattern, value_str)
            if match:
                return formatter(match)
        
        return value_str
    
    def _update_schema_config(self, table_name: str, chinese_title: str,
                            field_configs: List[Dict], table_type: str,
                            parent_table: Optional[str] = None):
        """更新 schema 配置"""
        try:
            # 加载现有配置
            config = self.config
            
            # 更新 tables
            if "tables" not in config:
                config["tables"] = {}
            
            config["tables"][table_name] = {
                "chinese_name": chinese_title or table_name,
                "type": table_type,
                "parent_table": parent_table,
                "fields": field_configs,
                "updated_at": datetime.now().isoformat()
            }
            
            # 更新 mappings
            if "mappings" not in config:
                config["mappings"] = {}
            
            for field in field_configs:
                source = field.get('sourceField') or field.get('chinese_name', '')
                target = field.get('targetField') or field.get('english_name', '')
                if source and target:
                    config["mappings"][source] = {
                        "target": target,
                        "table": table_name,
                        "data_type": field.get('dataType') or field.get('data_type', 'VARCHAR')
                    }
            
            # 保存配置
            with open(self.schema_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            
            print(f"已更新 schema 配置: {table_name}")
            
        except Exception as e:
            print(f"更新 schema 配置失败: {e}")
    
    def _update_navigation_config(self, table_name: str, chinese_title: str,
                                 module_id: str, module_name: str,
                                 table_type: str, parent_table: Optional[str] = None,
                                 sub_module_id: str = "", sub_module_name: str = ""):
        """更新导航配置"""
        print(f"\n[导航配置] 开始更新...")
        print(f"[导航配置] 参数: table_name={table_name}, chinese_title={chinese_title}")
        print(f"[导航配置] 参数: module_id={module_id}, module_name={module_name}")
        print(f"[导航配置] 参数: sub_module_id={sub_module_id}, sub_module_name={sub_module_name}")
        print(f"[导航配置] 配置文件路径: {self.navigation_file}")
        
        try:
            # 加载现有导航配置
            if os.path.exists(self.navigation_file):
                print(f"[导航配置] 文件存在，正在加载...")
                with open(self.navigation_file, 'r', encoding='utf-8') as f:
                    nav_config = json.load(f)
                print(f"[导航配置] 已加载，现有模块数: {len(nav_config.get('modules', []))}")
            else:
                print(f"[导航配置] 文件不存在，创建新配置")
                nav_config = {"modules": []}
            
            # 查找或创建模块
            module = None
            for m in nav_config.get("modules", []):
                if m.get("id") == module_id:
                    module = m
                    print(f"[导航配置] 找到现有模块: {module_id}")
                    break
            
            if not module:
                print(f"[导航配置] 创建新模块: {module_id}")
                module = {
                    "id": module_id,
                    "title": module_name,
                    "name": module_name,
                    "icon": "Folder",
                    "path": f"/{module_id}",
                    "type": "module",
                    "children": []
                }
                nav_config["modules"].append(module)
                print(f"[导航配置] 新模块已添加")
            
            # 确保模块有 children 字段
            if "children" not in module:
                module["children"] = []
            
            # 查找或创建子模块
            sub_module = None
            if sub_module_id:
                for sm in module.get("children", []):
                    if sm.get("id") == sub_module_id:
                        sub_module = sm
                        print(f"[导航配置] 找到现有子模块: {sub_module_id}")
                        break
                
                if not sub_module:
                    print(f"[导航配置] 创建新子模块: {sub_module_id}")
                    sub_module = {
                        "id": sub_module_id,
                        "title": sub_module_name,
                        "name": sub_module_name,
                        "icon": "Folder",
                        "path": f"/{module_id}/sub-{sub_module_id}",
                        "type": "module",
                        "children": []
                    }
                    module["children"].append(sub_module)
                    print(f"[导航配置] 新子模块已添加")
            
            # 构建表节点信息
            table_node = {
                "id": f"table-{table_name}",
                "title": chinese_title or table_name,
                "name": chinese_title or table_name,
                "icon": "Document",
                "path": f"/data/{table_name}",
                "type": "component",
                "component": "DynamicDataView",
                "api_endpoint": f"/api/data/{table_name}",
                "table_name": table_name,
                "table_type": table_type
            }
            
            # 添加表到子模块或模块
            target = sub_module if sub_module else module
            target_type = "子模块" if sub_module else "模块"
            target_id = sub_module_id if sub_module else module_id
            
            # 确保目标有 children 字段
            if "children" not in target:
                target["children"] = []
            
            existing = [t for t in target.get("children", []) if t.get("table_name") == table_name]
            if not existing:
                target["children"].append(table_node)
                print(f"[导航配置] 已添加表到{target_type} {target_id}: {chinese_title or table_name}")
            else:
                print(f"[导航配置] 表已存在，跳过: {chinese_title or table_name}")
            
            # 保存导航配置
            print(f"[导航配置] 正在保存到文件...")
            with open(self.navigation_file, 'w', encoding='utf-8') as f:
                json.dump(nav_config, f, ensure_ascii=False, indent=2)
            
            print(f"[导航配置] 保存成功！")
            
        except Exception as e:
            print(f"[导航配置] 更新失败: {e}")
            import traceback
            traceback.print_exc()
