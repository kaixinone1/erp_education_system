#!/usr/bin/env python3
"""
自动表管理框架 - 零配置方案
直接从数据库表结构读取字段信息，无需配置文件
"""
import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import APIRouter, HTTPException
from typing import Dict, List, Any, Optional
from datetime import datetime, date

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


class AutoTableManager:
    """自动表管理器 - 零配置"""
    
    def __init__(self, table_name: str):
        self.table_name = table_name
        self._schema = None
    
    def get_schema(self) -> List[Dict[str, Any]]:
        """从数据库读取表结构"""
        if self._schema is not None:
            return self._schema
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # 查询表结构
            cursor.execute("""
                SELECT 
                    column_name,
                    data_type,
                    is_nullable,
                    character_maximum_length,
                    column_default
                FROM information_schema.columns
                WHERE table_name = %s
                ORDER BY ordinal_position
            """, (self.table_name,))
            
            rows = cursor.fetchall()
            
            schema = []
            for row in rows:
                col_name = row[0]
                data_type = row[1]
                is_nullable = row[2] == 'YES'
                max_length = row[3]
                
                # 跳过系统字段
                if col_name in ['id', 'created_at', 'updated_at']:
                    continue
                
                # 映射字段类型
                field_type = self._map_data_type(data_type)
                
                schema.append({
                    'name': col_name,
                    'type': field_type,
                    'length': max_length,
                    'nullable': is_nullable,
                    'db_type': data_type
                })
            
            self._schema = schema
            return schema
            
        finally:
            cursor.close()
            conn.close()
    
    def _map_data_type(self, db_type: str) -> str:
        """映射数据库类型到前端类型"""
        type_mapping = {
            'character varying': 'VARCHAR',
            'text': 'TEXT',
            'integer': 'INTEGER',
            'bigint': 'INTEGER',
            'numeric': 'DECIMAL',
            'decimal': 'DECIMAL',
            'double precision': 'DECIMAL',
            'date': 'DATE',
            'timestamp without time zone': 'DATETIME',
            'timestamp with time zone': 'DATETIME',
            'boolean': 'BOOLEAN'
        }
        return type_mapping.get(db_type, 'VARCHAR')
    
    def get_data(self, filters: Dict = None, page: int = 1, page_size: int = 20) -> Dict:
        """获取数据"""
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        try:
            # 获取所有字段名
            schema = self.get_schema()
            field_names = ['"id"', '"teacher_id"'] + [f'"{f["name"]}"' for f in schema]
            
            # 构建查询
            sql = f"SELECT {', '.join(field_names)} FROM {self.table_name} WHERE 1=1"
            params = []
            
            if filters:
                for key, value in filters.items():
                    sql += f" AND \"{key}\" = %s"
                    params.append(value)
            
            # 获取总数
            count_sql = f"SELECT COUNT(*) FROM {self.table_name} WHERE 1=1"
            if filters:
                for key, value in filters.items():
                    count_sql += f" AND \"{key}\" = %s"
            
            cursor.execute(count_sql, params)
            count_row = cursor.fetchone()
            if count_row:
                # RealDictCursor 返回字典
                total = list(count_row.values())[0]
            else:
                total = 0
            
            # 分页
            sql += " ORDER BY updated_at DESC"
            sql += f" LIMIT {page_size} OFFSET {(page - 1) * page_size}"
            
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            
            return {
                'data': [dict(row) for row in rows],
                'total': total,
                'page': page,
                'page_size': page_size
            }
            
        finally:
            cursor.close()
            conn.close()
    
    def get_by_teacher_id(self, teacher_id: int) -> Optional[Dict]:
        """根据teacher_id获取单条数据"""
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        try:
            schema = self.get_schema()
            field_names = ['"id"', '"teacher_id"'] + [f'"{f["name"]}"' for f in schema]
            
            cursor.execute(f"""
                SELECT {', '.join(field_names)}
                FROM {self.table_name}
                WHERE teacher_id = %s
            """, (teacher_id,))
            
            row = cursor.fetchone()
            return dict(row) if row else None
            
        finally:
            cursor.close()
            conn.close()
    
    def update_data(self, teacher_id: int, data: Dict) -> bool:
        """更新数据"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # 获取表结构，只更新存在的字段
            schema = self.get_schema()
            valid_fields = {f['name'] for f in schema}
            
            updates = []
            values = []
            
            for key, value in data.items():
                if key in valid_fields and key not in ['id', 'teacher_id']:
                    updates.append(f'"{key}" = %s')
                    values.append(value)
            
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


# 全局表管理器缓存
_table_managers: Dict[str, AutoTableManager] = {}


def get_table_manager(table_name: str) -> AutoTableManager:
    """获取表管理器（带缓存）"""
    if table_name not in _table_managers:
        _table_managers[table_name] = AutoTableManager(table_name)
    return _table_managers[table_name]


def load_table_translation(table_name: str) -> dict:
    """加载表的中文翻译"""
    import json
    import os
    
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'table_translations.json')
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                translations = json.load(f)
                return translations.get('tables', {}).get(table_name, {})
    except Exception as e:
        print(f"加载翻译文件失败: {e}")
    
    return {}


def create_auto_table_routes(table_name: str) -> APIRouter:
    """为表创建自动API路由"""
    router = APIRouter(prefix=f"/api/auto-table/{table_name}")
    manager = get_table_manager(table_name)
    translation = load_table_translation(table_name)
    
    # 获取表结构
    @router.get("/schema")
    async def get_schema():
        """获取表结构"""
        schema = manager.get_schema()
        field_translations = translation.get('fields', {})
        
        # 创建字段映射
        schema_map = {field['name']: field for field in schema}
        
        # 按照翻译文件中定义的顺序排列字段
        ordered_schema = []
        for field_name in field_translations.keys():
            if field_name in schema_map:
                field = schema_map[field_name]
                field['label'] = field_translations[field_name]
                ordered_schema.append(field)
        
        # 添加翻译文件中没有的字段（如果有的话）
        for field in schema:
            if field['name'] not in field_translations:
                field['label'] = field['name']
                ordered_schema.append(field)
        
        return {
            "status": "success",
            "data": {
                "table_name": table_name,
                "chinese_name": translation.get('chinese_name', table_name),
                "description": translation.get('description', ''),
                "fields": ordered_schema
            }
        }
    
    # 列表查询
    @router.get("/list")
    async def list_data(
        page: int = 1,
        page_size: int = 20,
        teacher_id: int = None
    ):
        """获取数据列表"""
        filters = {}
        if teacher_id:
            filters['teacher_id'] = teacher_id
        
        result = manager.get_data(filters=filters if filters else None, page=page, page_size=page_size)
        
        return {
            "status": "success",
            **result
        }
    
    # 获取单条
    @router.get("/detail/{teacher_id}")
    async def get_detail(teacher_id: int):
        """获取单条数据详情"""
        data = manager.get_by_teacher_id(teacher_id)
        if not data:
            raise HTTPException(status_code=404, detail="数据不存在")
        
        return {
            "status": "success",
            "data": data
        }
    
    # 更新
    @router.put("/update/{teacher_id}")
    async def update_data(teacher_id: int, data: Dict[str, Any]):
        """更新数据"""
        success = manager.update_data(teacher_id, data)
        if success:
            return {"status": "success", "message": "更新成功"}
        else:
            raise HTTPException(status_code=500, detail="更新失败")
    
    # 删除
    @router.delete("/delete/{teacher_id}")
    async def delete_data(teacher_id: int):
        """删除数据"""
        success = manager.delete_data(teacher_id)
        if success:
            return {"status": "success", "message": "删除成功"}
        else:
            raise HTTPException(status_code=500, detail="删除失败")
    
    # 计算工作年限（退休表专用）
    if table_name == 'retirement_report_data':
        @router.post("/calculate/{teacher_id}")
        async def calculate(teacher_id: int):
            """计算退休信息"""
            from utils.retirement_calculator import calculate_retirement_info
            
            data = manager.get_by_teacher_id(teacher_id)
            if not data:
                raise HTTPException(status_code=404, detail="数据不存在")
            
            birth_date = data.get('出生日期')
            gender = data.get('性别')
            personal_identity = data.get('个人身份', '干部')
            work_start_date = data.get('参加工作时间')
            
            if not birth_date or not gender or not work_start_date:
                raise HTTPException(status_code=400, detail="缺少必要的计算参数")
            
            # 转换日期
            if isinstance(birth_date, str):
                birth_date = datetime.strptime(birth_date, '%Y-%m-%d').date()
            if isinstance(work_start_date, str):
                work_start_date = datetime.strptime(work_start_date, '%Y-%m-%d').date()
            
            result = calculate_retirement_info(
                birth_date=birth_date,
                gender=gender,
                personal_identity=personal_identity,
                work_start_date=work_start_date
            )
            
            return {
                "status": "success",
                "data": {
                    "original_retirement_date": str(result['original_retirement_date']),
                    "delay_months": result['delay_months'],
                    "calculated_retirement_date": str(result['calculated_retirement_date']),
                    "actual_retirement_date": str(result['actual_retirement_date']),
                    "work_years": result['work_years']
                }
            }
        
        @router.post("/save-calculation/{teacher_id}")
        async def save_calculation(teacher_id: int, data: Dict[str, Any]):
            """保存计算结果"""
            retirement_date = data.get('retirement_date')
            work_years = data.get('work_years')
            
            if not retirement_date or work_years is None:
                raise HTTPException(status_code=400, detail="缺少退休日期或工作年限")
            
            success = manager.update_data(teacher_id, {
                '退休时间': retirement_date,
                '工作年限': work_years
            })
            
            if success:
                return {"status": "success", "message": "保存成功"}
            else:
                raise HTTPException(status_code=500, detail="保存失败")
    
    return router


# 创建通用动态路由
from fastapi import Request

def create_dynamic_auto_table_router() -> APIRouter:
    """创建通用动态路由处理器 - 支持任意表名"""
    router = APIRouter(prefix="/api/auto-table")
    
    @router.get("/{table_name}/schema")
    async def dynamic_schema(table_name: str):
        """动态获取任意表的结构"""
        try:
            manager = get_table_manager(table_name)
            schema = manager.get_schema()
            translation = load_table_translation(table_name)
            field_translations = translation.get('fields', {})
            
            # 创建字段映射
            schema_map = {field['name']: field for field in schema}
            
            # 按照翻译文件中定义的顺序排列字段
            ordered_schema = []
            for field_name in field_translations.keys():
                if field_name in schema_map:
                    field = schema_map[field_name]
                    field['label'] = field_translations[field_name]
                    ordered_schema.append(field)
            
            # 添加翻译文件中没有的字段
            for field in schema:
                if field['name'] not in field_translations:
                    field['label'] = field['name']
                    ordered_schema.append(field)
            
            return {
                "status": "success",
                "data": {
                    "table_name": table_name,
                    "chinese_name": translation.get('chinese_name', table_name),
                    "description": translation.get('description', ''),
                    "fields": ordered_schema
                }
            }
        except Exception as e:
            raise HTTPException(status_code=404, detail=f"表不存在或无法访问: {e}")
    
    @router.get("/{table_name}/list")
    async def dynamic_list(
        table_name: str,
        page: int = 1,
        page_size: int = 20,
        teacher_id: int = None
    ):
        """动态获取任意表的数据列表"""
        try:
            manager = get_table_manager(table_name)
            filters = {}
            if teacher_id:
                filters['teacher_id'] = teacher_id
            
            result = manager.get_data(filters=filters if filters else None, page=page, page_size=page_size)
            
            return {
                "status": "success",
                **result
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"获取数据失败: {e}")
    
    @router.get("/{table_name}/detail/{teacher_id}")
    async def dynamic_detail(table_name: str, teacher_id: int):
        """动态获取单条数据详情"""
        try:
            manager = get_table_manager(table_name)
            data = manager.get_by_teacher_id(teacher_id)
            if not data:
                raise HTTPException(status_code=404, detail="数据不存在")
            
            return {
                "status": "success",
                "data": data
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"获取详情失败: {e}")
    
    @router.put("/{table_name}/update/{teacher_id}")
    async def dynamic_update(table_name: str, teacher_id: int, data: Dict[str, Any]):
        """动态更新数据"""
        try:
            manager = get_table_manager(table_name)
            success = manager.update_data(teacher_id, data)
            if success:
                return {"status": "success", "message": "更新成功"}
            else:
                raise HTTPException(status_code=500, detail="更新失败")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"更新失败: {e}")
    
    @router.delete("/{table_name}/delete/{teacher_id}")
    async def dynamic_delete(table_name: str, teacher_id: int):
        """动态删除数据"""
        try:
            manager = get_table_manager(table_name)
            success = manager.delete_data(teacher_id)
            if success:
                return {"status": "success", "message": "删除成功"}
            else:
                raise HTTPException(status_code=500, detail="删除失败")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"删除失败: {e}")
    
    return router
