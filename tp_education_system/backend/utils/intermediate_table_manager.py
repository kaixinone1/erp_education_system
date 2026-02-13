#!/usr/bin/env python3
"""
中间表管理模块
用于管理动态创建的中间表
"""
import psycopg2
import json
import os
from datetime import datetime
from fastapi import APIRouter, HTTPException
from typing import Dict, List, Any

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


def get_translation_path() -> str:
    """获取翻译文件路径"""
    return os.path.join(os.path.dirname(__file__), '..', 'config', 'table_translations.json')


def load_all_translations() -> Dict:
    """加载所有表翻译"""
    config_path = get_translation_path()
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"加载翻译文件失败: {e}")
    return {"tables": {}}


def save_translations(data: Dict):
    """保存翻译文件"""
    config_path = get_translation_path()
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"保存翻译文件失败: {e}")
        return False


class IntermediateTableManager:
    """中间表管理器"""
    
    @staticmethod
    def get_all_tables() -> List[Dict]:
        """获取所有中间表列表"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # 查询所有以_data结尾的表（中间表命名约定）
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_type = 'BASE TABLE'
                AND (table_name LIKE '%_data' OR table_name LIKE '%_records')
                ORDER BY table_name
            """)
            
            tables = []
            translations = load_all_translations()
            
            for row in cursor.fetchall():
                table_name = row[0]
                translation = translations.get('tables', {}).get(table_name, {})
                
                # 获取字段数量
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM information_schema.columns 
                    WHERE table_name = %s
                """, (table_name,))
                field_count = cursor.fetchone()[0]
                
                tables.append({
                    'table_name': table_name,
                    'chinese_name': translation.get('chinese_name', table_name),
                    'description': translation.get('description', ''),
                    'field_count': field_count - 3,  # 减去id, created_at, updated_at
                    'created_at': datetime.now().isoformat()  # 暂时用当前时间
                })
            
            return tables
            
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def create_table(table_name: str, chinese_name: str, fields: List[Dict]) -> bool:
        """创建新的中间表"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # 构建建表SQL
            columns = [
                "id SERIAL PRIMARY KEY",
                "teacher_id INTEGER REFERENCES teacher_basic_info(id)"
            ]
            
            field_translations = {}
            for field in fields:
                field_name = field['name']
                field_type = field['type']
                field_label = field.get('label', field_name)
                
                # 映射字段类型
                if field_type == 'VARCHAR':
                    length = field.get('length', 50)
                    sql_type = f"VARCHAR({length})"
                elif field_type == 'TEXT':
                    sql_type = "TEXT"
                elif field_type == 'INTEGER':
                    sql_type = "INTEGER"
                elif field_type == 'DECIMAL':
                    sql_type = "DECIMAL(10,2)"
                elif field_type == 'DATE':
                    sql_type = "DATE"
                elif field_type == 'BOOLEAN':
                    sql_type = "BOOLEAN"
                else:
                    sql_type = "VARCHAR(50)"
                
                nullable = "NOT NULL" if field.get('required') else ""
                columns.append(f'"{field_name}" {sql_type} {nullable}'.strip())
                field_translations[field_name] = field_label
            
            columns.extend([
                "created_at TIMESTAMP DEFAULT NOW()",
                "updated_at TIMESTAMP DEFAULT NOW()"
            ])
            
            # 执行建表
            create_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(columns)})"
            cursor.execute(create_sql)
            
            # 保存翻译
            translations = load_all_translations()
            if 'tables' not in translations:
                translations['tables'] = {}
            
            translations['tables'][table_name] = {
                'chinese_name': chinese_name,
                'description': f'{chinese_name}中间表',
                'fields': field_translations
            }
            
            save_translations(translations)
            
            conn.commit()
            return True
            
        except Exception as e:
            conn.rollback()
            print(f"创建表失败: {e}")
            return False
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def delete_table(table_name: str) -> bool:
        """删除中间表"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # 删除表
            cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
            
            # 删除翻译
            translations = load_all_translations()
            if table_name in translations.get('tables', {}):
                del translations['tables'][table_name]
                save_translations(translations)
            
            conn.commit()
            return True
            
        except Exception as e:
            conn.rollback()
            print(f"删除表失败: {e}")
            return False
        finally:
            cursor.close()
            conn.close()


# 创建API路由
def create_intermediate_table_manager_routes() -> APIRouter:
    """创建中间表管理API路由"""
    router = APIRouter(prefix="/api/intermediate-tables")
    manager = IntermediateTableManager()
    
    # 获取所有中间表列表
    @router.get("/list")
    async def list_tables():
        """获取所有中间表列表"""
        tables = manager.get_all_tables()
        return {
            "status": "success",
            "data": tables
        }
    
    # 创建新中间表
    @router.post("/create")
    async def create_table(data: Dict[str, Any]):
        """创建新的中间表"""
        table_name = data.get('table_name')
        chinese_name = data.get('chinese_name')
        fields = data.get('fields', [])
        
        if not table_name or not chinese_name:
            raise HTTPException(status_code=400, detail="表名和中文名不能为空")
        
        if not fields:
            raise HTTPException(status_code=400, detail="至少需要定义一个字段")
        
        success = manager.create_table(table_name, chinese_name, fields)
        if success:
            return {
                "status": "success",
                "message": "中间表创建成功",
                "data": {
                    "table_name": table_name,
                    "access_url": f"/auto-table/{table_name}"
                }
            }
        else:
            raise HTTPException(status_code=500, detail="创建表失败")
    
    # 删除中间表
    @router.delete("/{table_name}")
    async def delete_table(table_name: str):
        """删除中间表"""
        success = manager.delete_table(table_name)
        if success:
            return {
                "status": "success",
                "message": "中间表删除成功"
            }
        else:
            raise HTTPException(status_code=500, detail="删除表失败")
    
    return router
