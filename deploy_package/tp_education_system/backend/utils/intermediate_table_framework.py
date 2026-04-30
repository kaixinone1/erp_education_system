#!/usr/bin/env python3
"""
通用中间表框架 - 后端引擎
实现配置驱动的中间表管理
"""
import json
import os
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, date
from fastapi import APIRouter, HTTPException, Query
import psycopg2
from psycopg2.extras import RealDictCursor

# 数据库配置
DATABASE_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "database": "taiping_education",
    "user": "taiping_user",
    "password": "taiping_password"
}


def get_db_connection():
    """获取数据库连接"""
    return psycopg2.connect(**DATABASE_CONFIG)


class IntermediateTableConfig:
    """中间表配置类"""
    
    def __init__(self, config_path: str):
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
    
    @property
    def table_name(self) -> str:
        return self.config['table_name']
    
    @property
    def chinese_name(self) -> str:
        return self.config.get('chinese_name', self.table_name)
    
    @property
    def fields(self) -> List[Dict]:
        return self.config.get('fields', [])
    
    @property
    def calculations(self) -> Dict:
        return self.config.get('calculations', {})
    
    @property
    def features(self) -> Dict:
        return self.config.get('features', {
            'crud': True,
            'export': [],
            'calculator': False,
            'import': False
        })
    
    def get_field(self, name: str) -> Optional[Dict]:
        """获取字段配置"""
        for field in self.fields:
            if field['name'] == name:
                return field
        return None
    
    def get_source_fields(self) -> List[Dict]:
        """获取有数据源的字段"""
        return [f for f in self.fields if 'source' in f]
    
    def get_calculated_fields(self) -> List[Dict]:
        """获取计算字段"""
        return [f for f in self.fields if f.get('calculated', False)]


class IntermediateTableEngine:
    """通用中间表引擎"""
    
    def __init__(self, config: IntermediateTableConfig):
        self.config = config
        self.table_name = config.table_name
    
    def ensure_table_exists(self):
        """确保中间表存在，不存在则创建"""
        # 如果是现有表，不创建
        if self.config.config.get('existing_table', False):
            print(f"使用现有表: {self.table_name}")
            return
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # 检查表是否存在
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = %s
                )
            """, (self.table_name,))
            
            exists = cursor.fetchone()[0]
            
            if not exists:
                # 创建表
                self._create_table(cursor)
                conn.commit()
                print(f"创建中间表: {self.table_name}")
        finally:
            cursor.close()
            conn.close()
    
    def _create_table(self, cursor):
        """创建中间表"""
        fields_sql = []
        
        for field in self.config.fields:
            name = field['name']
            field_type = field['type']
            length = field.get('length')
            required = field.get('required', False)
            
            # 映射类型
            if field_type == 'VARCHAR':
                sql_type = f"VARCHAR({length or 255})"
            elif field_type == 'INTEGER':
                sql_type = "INTEGER"
            elif field_type == 'DECIMAL':
                sql_type = "DECIMAL(10,2)"
            elif field_type == 'DATE':
                sql_type = "DATE"
            elif field_type == 'DATETIME':
                sql_type = "TIMESTAMP"
            elif field_type == 'BOOLEAN':
                sql_type = "BOOLEAN"
            elif field_type == 'TEXT':
                sql_type = "TEXT"
            else:
                sql_type = "VARCHAR(255)"
            
            nullable = "NOT NULL" if required else ""
            fields_sql.append(f'"{name}" {sql_type} {nullable}')
        
        # 添加系统字段
        fields_sql.extend([
            '"id" SERIAL PRIMARY KEY',
            '"teacher_id" INTEGER',
            '"created_at" TIMESTAMP DEFAULT NOW()',
            '"updated_at" TIMESTAMP DEFAULT NOW()'
        ])
        
        create_sql = f"""
            CREATE TABLE {self.table_name} (
                {', '.join(fields_sql)}
            )
        """
        
        cursor.execute(create_sql)
        
        # 创建索引
        cursor.execute(f"""
            CREATE INDEX idx_{self.table_name}_teacher_id 
            ON {self.table_name}(teacher_id)
        """)
    
    def aggregate_data(self, teacher_id: int) -> Dict[str, Any]:
        """从多个源表聚合数据"""
        # 如果是现有表，直接从表中获取数据
        if self.config.config.get('existing_table', False):
            return self._get_data_from_existing_table(teacher_id)
        
        result = {'teacher_id': teacher_id}
        
        # 按源表分组
        sources = {}
        for field in self.config.get_source_fields():
            source_table = field['source']['table']
            source_field = field['source']['field']
            target_field = field['name']
            
            if source_table not in sources:
                sources[source_table] = []
            sources[source_table].append((source_field, target_field))
        
        # 从每个源表查询
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            for table, mappings in sources.items():
                fields_sql = ', '.join([f"{m[0]} as {m[1]}" for m in mappings])
                
                cursor.execute(f"""
                    SELECT {fields_sql}
                    FROM {table}
                    WHERE id = %s
                """, (teacher_id,))
                
                row = cursor.fetchone()
                if row:
                    for i, (_, target) in enumerate(mappings):
                        result[target] = row[i]
        finally:
            cursor.close()
            conn.close()
        
        return result
    
    def _get_data_from_existing_table(self, teacher_id: int) -> Dict[str, Any]:
        """从现有中间表获取数据"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # 获取所有字段
            field_names = [f'"{f["name"]}"' for f in self.config.fields]
            
            cursor.execute(f"""
                SELECT {', '.join(field_names)}
                FROM {self.table_name}
                WHERE teacher_id = %s
            """, (teacher_id,))
            
            row = cursor.fetchone()
            if row:
                result = {'teacher_id': teacher_id}
                for i, field in enumerate(self.config.fields):
                    result[field['name']] = row[i]
                return result
            else:
                return {'teacher_id': teacher_id}
                
        finally:
            cursor.close()
            conn.close()
    
    def calculate_fields(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """计算派生字段"""
        result = data.copy()
        
        for calc_name, calc_config in self.config.calculations.items():
            calc_type = calc_config.get('type')
            
            if calc_type == 'retirement':
                # 退休计算
                from utils.retirement_calculator import calculate_retirement_info
                
                birth_date = data.get('出生日期')
                gender = data.get('性别')
                personal_identity = data.get('个人身份', '干部')
                work_start_date = data.get('参加工作时间')
                
                if birth_date and gender and work_start_date:
                    # 转换日期
                    if isinstance(birth_date, str):
                        birth_date = datetime.strptime(birth_date, '%Y-%m-%d').date()
                    if isinstance(work_start_date, str):
                        work_start_date = datetime.strptime(work_start_date, '%Y-%m-%d').date()
                    
                    calc_result = calculate_retirement_info(
                        birth_date=birth_date,
                        gender=gender,
                        personal_identity=personal_identity,
                        work_start_date=work_start_date
                    )
                    
                    # 更新计算结果
                    result['原退休日期'] = str(calc_result['original_retirement_date'])
                    result['延迟月数'] = calc_result['delay_months']
                    result['现退休日期'] = str(calc_result['actual_retirement_date'])
                    result['工作年限'] = calc_result['work_years']
        
        return result
    
    def save_data(self, data: Dict[str, Any]) -> bool:
        """保存数据到中间表"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            teacher_id = data.get('teacher_id')
            
            # 如果是现有表，使用UPDATE而不是UPSERT
            if self.config.config.get('existing_table', False):
                return self._update_existing_table(cursor, conn, teacher_id, data)
            
            # 构建字段和值
            field_names = []
            field_values = []
            updates = []
            
            for field in self.config.fields:
                name = field['name']
                if name in data:
                    field_names.append(f'"{name}"')
                    field_values.append(data[name])
                    updates.append(f'"{name}" = EXCLUDED."{name}"')
            
            # 添加系统字段
            field_names.extend(['"teacher_id"', '"updated_at"'])
            field_values.extend([teacher_id, datetime.now()])
            
            # 使用 UPSERT
            sql = f"""
                INSERT INTO {self.table_name} ({', '.join(field_names)})
                VALUES ({', '.join(['%s'] * len(field_values))})
                ON CONFLICT (teacher_id) DO UPDATE SET
                    {', '.join(updates)},
                    updated_at = NOW()
            """
            
            cursor.execute(sql, field_values)
            conn.commit()
            return True
            
        except Exception as e:
            conn.rollback()
            print(f"保存失败: {e}")
            return False
        finally:
            cursor.close()
            conn.close()
    
    def _update_existing_table(self, cursor, conn, teacher_id: int, data: Dict[str, Any]) -> bool:
        """更新现有表中的数据"""
        try:
            # 只更新提供的字段
            updates = []
            values = []
            
            for field in self.config.fields:
                name = field['name']
                if name in data and data[name] is not None:
                    updates.append(f'"{name}" = %s')
                    values.append(data[name])
            
            if not updates:
                return True
            
            values.append(teacher_id)
            
            sql = f"""
                UPDATE {self.table_name}
                SET {', '.join(updates)}, updated_at = NOW()
                WHERE teacher_id = %s
            """
            
            cursor.execute(sql, values)
            conn.commit()
            return cursor.rowcount > 0
            
        except Exception as e:
            conn.rollback()
            print(f"更新现有表失败: {e}")
            return False
    
    def get_data(self, teacher_id: int = None, filters: Dict = None) -> List[Dict]:
        """获取数据"""
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        try:
            field_names = [f'"{f["name"]}"' for f in self.config.fields]
            field_names.extend(['"id"', '"teacher_id"', '"created_at"', '"updated_at"'])
            
            sql = f"SELECT {', '.join(field_names)} FROM {self.table_name} WHERE 1=1"
            params = []
            
            if teacher_id:
                sql += " AND teacher_id = %s"
                params.append(teacher_id)
            
            if filters:
                for key, value in filters.items():
                    sql += f" AND \"{key}\" = %s"
                    params.append(value)
            
            sql += " ORDER BY updated_at DESC"
            
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            
            return [dict(row) for row in rows]
            
        finally:
            cursor.close()
            conn.close()
    
    def update_data(self, teacher_id: int, data: Dict[str, Any]) -> bool:
        """更新数据"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            updates = []
            params = []
            
            for field in self.config.fields:
                name = field['name']
                if name in data:
                    updates.append(f'"{name}" = %s')
                    params.append(data[name])
            
            if not updates:
                return False
            
            params.append(teacher_id)
            
            sql = f"""
                UPDATE {self.table_name}
                SET {', '.join(updates)}, updated_at = NOW()
                WHERE teacher_id = %s
            """
            
            cursor.execute(sql, params)
            conn.commit()
            return cursor.rowcount > 0
            
        except Exception as e:
            conn.rollback()
            print(f"更新失败: {e}")
            return False
        finally:
            cursor.close()
            conn.close()
    
    def delete_data(self, teacher_id: int) -> bool:
        """删除数据"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(f"""
                DELETE FROM {self.table_name}
                WHERE teacher_id = %s
            """, (teacher_id,))
            
            conn.commit()
            return cursor.rowcount > 0
            
        except Exception as e:
            conn.rollback()
            print(f"删除失败: {e}")
            return False
        finally:
            cursor.close()
            conn.close()


# 全局注册表
_registered_tables: Dict[str, IntermediateTableEngine] = {}


def register_intermediate_table(config_path: str) -> IntermediateTableEngine:
    """注册中间表"""
    config = IntermediateTableConfig(config_path)
    engine = IntermediateTableEngine(config)
    
    # 确保表存在
    engine.ensure_table_exists()
    
    # 注册到全局
    _registered_tables[config.table_name] = engine
    
    print(f"注册中间表: {config.table_name} ({config.chinese_name})")
    return engine


def get_intermediate_table_engine(table_name: str) -> Optional[IntermediateTableEngine]:
    """获取已注册的中间表引擎"""
    return _registered_tables.get(table_name)


def create_intermediate_table_routes(table_name: str) -> APIRouter:
    """为中间表创建API路由"""
    engine = get_intermediate_table_engine(table_name)
    if not engine:
        raise ValueError(f"未找到中间表: {table_name}")
    
    config = engine.config
    router = APIRouter(prefix=f"/api/intermediate/{table_name}")
    
    features = config.features
    
    # 获取配置
    @router.get("/config")
    async def get_config():
        """获取中间表配置"""
        return {
            "status": "success",
            "data": {
                "table_name": config.table_name,
                "chinese_name": config.chinese_name,
                "description": config.config.get('description', ''),
                "fields": config.fields,
                "features": config.features,
                "calculations": config.calculations,
                "display": config.config.get('display', {})
            }
        }
    
    # 列表查询
    @router.get("/list")
    async def list_data(
        teacher_id: int = Query(None),
        page: int = Query(1),
        page_size: int = Query(20)
    ):
        """获取数据列表"""
        filters = {}
        if teacher_id:
            filters['teacher_id'] = teacher_id
        
        data = engine.get_data(filters=filters if filters else None)
        
        # 分页
        total = len(data)
        start = (page - 1) * page_size
        end = start + page_size
        page_data = data[start:end]
        
        return {
            "status": "success",
            "data": page_data,
            "total": total,
            "page": page,
            "page_size": page_size
        }
    
    # 获取单条
    @router.get("/detail/{teacher_id}")
    async def get_detail(teacher_id: int):
        """获取单条数据详情"""
        data = engine.get_data(teacher_id=teacher_id)
        if not data:
            raise HTTPException(status_code=404, detail="数据不存在")
        
        return {
            "status": "success",
            "data": data[0]
        }
    
    # 创建/更新
    if features.get('crud', True):
        @router.post("/save")
        async def save_data(data: Dict[str, Any]):
            """保存数据"""
            success = engine.save_data(data)
            if success:
                return {"status": "success", "message": "保存成功"}
            else:
                raise HTTPException(status_code=500, detail="保存失败")
        
        @router.put("/update/{teacher_id}")
        async def update_data(teacher_id: int, data: Dict[str, Any]):
            """更新数据"""
            success = engine.update_data(teacher_id, data)
            if success:
                return {"status": "success", "message": "更新成功"}
            else:
                raise HTTPException(status_code=500, detail="更新失败")
        
        @router.delete("/delete/{teacher_id}")
        async def delete_data(teacher_id: int):
            """删除数据"""
            success = engine.delete_data(teacher_id)
            if success:
                return {"status": "success", "message": "删除成功"}
            else:
                raise HTTPException(status_code=500, detail="删除失败")
    
    # 数据聚合
    @router.post("/aggregate/{teacher_id}")
    async def aggregate(teacher_id: int):
        """从源表聚合数据"""
        data = engine.aggregate_data(teacher_id)
        return {
            "status": "success",
            "data": data
        }
    
    # 计算
    if features.get('calculator', False):
        @router.post("/calculate/{teacher_id}")
        async def calculate(teacher_id: int, request_data: Dict[str, Any] = None):
            """计算派生字段"""
            # 先聚合数据
            data = engine.aggregate_data(teacher_id)
            # 再计算
            result = engine.calculate_fields(data)
            return {
                "status": "success",
                "data": result
            }
        
        @router.post("/save-retirement-calculation/{teacher_id}")
        async def save_retirement_calculation(teacher_id: int, data: Dict[str, Any]):
            """保存退休计算结果"""
            retirement_date = data.get('retirement_date')
            work_years = data.get('work_years')
            
            if not retirement_date or work_years is None:
                raise HTTPException(status_code=400, detail="缺少退休日期或工作年限")
            
            # 更新到中间表
            success = engine.save_data({
                'teacher_id': teacher_id,
                '退休时间': retirement_date,
                '工作年限': work_years
            })
            
            if success:
                return {"status": "success", "message": "退休计算结果已保存"}
            else:
                raise HTTPException(status_code=500, detail="保存失败")
    
    return router
