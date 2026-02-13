from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
import json
import os
from sqlalchemy import create_engine, text

router = APIRouter(prefix="/api/table-structure", tags=["table-structure"])

# 数据库连接
DATABASE_URL = "postgresql://taiping_user:taiping_password@localhost:5432/taiping_education"
engine = create_engine(DATABASE_URL)

# 配置文件路径
CONFIG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config')
SCHEMA_FILE = os.path.join(CONFIG_DIR, 'merged_schema_mappings.json')
FIELD_MAPPINGS_FILE = os.path.join(CONFIG_DIR, 'field_mappings.json')
TABLE_SCHEMAS_FILE = os.path.join(CONFIG_DIR, 'table_schemas.json')


def read_json_file(file_path: str) -> Optional[Dict[str, Any]]:
    """读取JSON文件"""
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    except Exception as e:
        print(f"读取文件失败 {file_path}: {e}")
        return {}


def write_json_file(file_path: str, data: Dict[str, Any]):
    """写入JSON文件"""
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"写入文件失败 {file_path}: {e}")
        return False


@router.get("/tables")
async def get_all_tables():
    """获取所有表列表"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_type = 'BASE TABLE'
                ORDER BY table_name
            """))
            tables = [row.table_name for row in result]
            
        # 获取表的中文名称
        config = read_json_file(SCHEMA_FILE)
        table_info = []
        
        for table_name in tables:
            table_config = config.get("tables", {}).get(table_name, {})
            chinese_name = table_config.get("chinese_name", table_name)
            table_info.append({
                "name": table_name,
                "chinese_name": chinese_name,
                "type": table_config.get("type", "master")
            })
        
        return {"tables": table_info}
    except Exception as e:
        print(f"获取表列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取表列表失败: {str(e)}")


@router.get("/{table_name}")
async def get_table_structure(table_name: str):
    """获取表结构详情"""
    try:
        with engine.connect() as conn:
            # 获取列信息
            result = conn.execute(text("""
                SELECT 
                    column_name,
                    data_type,
                    is_nullable,
                    character_maximum_length,
                    column_default,
                    ordinal_position
                FROM information_schema.columns
                WHERE table_name = :table_name AND table_schema = 'public'
                ORDER BY ordinal_position
            """), {"table_name": table_name})
            
            columns = []
            for row in result:
                columns.append({
                    "name": row.column_name,
                    "data_type": row.data_type,
                    "is_nullable": row.is_nullable == "YES",
                    "max_length": row.character_maximum_length,
                    "default_value": row.column_default,
                    "ordinal_position": row.ordinal_position
                })
            
            # 获取主键信息
            pk_result = conn.execute(text("""
                SELECT kcu.column_name
                FROM information_schema.table_constraints tc
                JOIN information_schema.key_column_usage kcu 
                    ON tc.constraint_name = kcu.constraint_name
                WHERE tc.table_name = :table_name 
                AND tc.constraint_type = 'PRIMARY KEY'
            """), {"table_name": table_name})
            
            primary_keys = [row.column_name for row in pk_result]
            
            # 获取索引信息
            index_result = conn.execute(text("""
                SELECT indexname, indexdef
                FROM pg_indexes
                WHERE tablename = :table_name
            """), {"table_name": table_name})
            
            indexes = []
            for row in index_result:
                indexes.append({
                    "name": row.indexname,
                    "definition": row.indexdef
                })
            
            # 获取配置信息
            config = read_json_file(SCHEMA_FILE)
            table_config = config.get("tables", {}).get(table_name, {})
            
            return {
                "table_name": table_name,
                "chinese_name": table_config.get("chinese_name", table_name),
                "columns": columns,
                "primary_keys": primary_keys,
                "indexes": indexes,
                "config": table_config
            }
    except Exception as e:
        print(f"获取表结构失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取表结构失败: {str(e)}")


@router.put("/{table_name}/field/{field_name}")
async def update_field(table_name: str, field_name: str, data: Dict[str, Any]):
    """更新字段信息"""
    try:
        # 读取现有配置
        config = read_json_file(SCHEMA_FILE)
        
        if "tables" not in config:
            config["tables"] = {}
        
        if table_name not in config["tables"]:
            config["tables"][table_name] = {}
        
        table_config = config["tables"][table_name]
        
        if "fields" not in table_config:
            table_config["fields"] = []
        
        # 查找并更新字段
        fields = table_config["fields"]
        field_found = False
        
        for field in fields:
            if field.get("name") == field_name:
                # 更新字段属性
                if "chinese_name" in data:
                    field["chinese_name"] = data["chinese_name"]
                if "type" in data:
                    field["type"] = data["type"]
                if "length" in data:
                    field["length"] = data["length"]
                if "required" in data:
                    field["required"] = data["required"]
                if "unique" in data:
                    field["unique"] = data["unique"]
                if "indexed" in data:
                    field["indexed"] = data["indexed"]
                field_found = True
                break
        
        # 如果字段不存在，添加新字段
        if not field_found:
            new_field = {
                "name": field_name,
                "chinese_name": data.get("chinese_name", field_name),
                "type": data.get("type", "VARCHAR"),
                "length": data.get("length", 255),
                "required": data.get("required", False),
                "unique": data.get("unique", False),
                "indexed": data.get("indexed", False)
            }
            fields.append(new_field)
        
        # 保存配置
        if write_json_file(SCHEMA_FILE, config):
            return {
                "status": "success",
                "message": f"字段 {field_name} 更新成功"
            }
        else:
            raise HTTPException(status_code=500, detail="保存配置失败")
    except Exception as e:
        print(f"更新字段失败: {e}")
        raise HTTPException(status_code=500, detail=f"更新字段失败: {str(e)}")


@router.post("/{table_name}/field")
async def add_field(table_name: str, data: Dict[str, Any]):
    """添加新字段"""
    try:
        field_name = data.get("name")
        field_type = data.get("type", "VARCHAR")
        
        if not field_name:
            raise HTTPException(status_code=400, detail="字段名称不能为空")
        
        # 构建ALTER TABLE语句
        with engine.connect() as conn:
            # 检查字段是否已存在
            check_result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = :table_name 
                AND column_name = :field_name
            """), {"table_name": table_name, "field_name": field_name})
            
            if check_result.fetchone():
                raise HTTPException(status_code=400, detail=f"字段 {field_name} 已存在")
            
            # 构建字段类型
            if field_type == "VARCHAR":
                length = data.get("length", 255)
                column_def = f"{field_name} VARCHAR({length})"
            elif field_type == "INTEGER":
                column_def = f"{field_name} INTEGER"
            elif field_type == "DECIMAL":
                column_def = f"{field_name} DECIMAL(10,2)"
            elif field_type == "DATE":
                column_def = f"{field_name} DATE"
            elif field_type == "DATETIME":
                column_def = f"{field_name} TIMESTAMP"
            elif field_type == "BOOLEAN":
                column_def = f"{field_name} BOOLEAN"
            elif field_type == "TEXT":
                column_def = f"{field_name} TEXT"
            else:
                column_def = f"{field_name} VARCHAR(255)"
            
            # 添加NULL约束
            if data.get("required", False):
                column_def += " NOT NULL"
            else:
                column_def += " NULL"
            
            # 执行ALTER TABLE
            alter_sql = f"ALTER TABLE {table_name} ADD COLUMN {column_def}"
            conn.execute(text(alter_sql))
            conn.commit()
        
        # 更新配置文件
        config = read_json_file(SCHEMA_FILE)
        if "tables" not in config:
            config["tables"] = {}
        
        if table_name not in config["tables"]:
            config["tables"][table_name] = {}
        
        table_config = config["tables"][table_name]
        if "fields" not in table_config:
            table_config["fields"] = []
        
        # 添加字段配置
        new_field = {
            "name": field_name,
            "chinese_name": data.get("chinese_name", field_name),
            "type": field_type,
            "length": data.get("length", 255),
            "required": data.get("required", False),
            "unique": data.get("unique", False),
            "indexed": data.get("indexed", False)
        }
        table_config["fields"].append(new_field)
        
        # 保存配置
        write_json_file(SCHEMA_FILE, config)
        
        return {
            "status": "success",
            "message": f"字段 {field_name} 添加成功"
        }
    except Exception as e:
        print(f"添加字段失败: {e}")
        raise HTTPException(status_code=500, detail=f"添加字段失败: {str(e)}")


@router.delete("/{table_name}/field/{field_name}")
async def delete_field(table_name: str, field_name: str):
    """删除字段"""
    try:
        # 检查是否为系统字段
        system_fields = ['id', 'created_at', 'updated_at', 'import_batch', 'code']
        if field_name.lower() in system_fields:
            raise HTTPException(status_code=400, detail=f"不能删除系统字段 {field_name}")
        
        with engine.connect() as conn:
            # 检查字段是否存在
            check_result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = :table_name 
                AND column_name = :field_name
            """), {"table_name": table_name, "field_name": field_name})
            
            if not check_result.fetchone():
                raise HTTPException(status_code=404, detail=f"字段 {field_name} 不存在")
            
            # 执行ALTER TABLE DROP COLUMN
            alter_sql = f"ALTER TABLE {table_name} DROP COLUMN {field_name}"
            conn.execute(text(alter_sql))
            conn.commit()
        
        # 更新配置文件
        config = read_json_file(SCHEMA_FILE)
        if "tables" in config and table_name in config["tables"]:
            table_config = config["tables"][table_name]
            if "fields" in table_config:
                table_config["fields"] = [
                    f for f in table_config["fields"] 
                    if f.get("name") != field_name
                ]
                write_json_file(SCHEMA_FILE, config)
        
        return {
            "status": "success",
            "message": f"字段 {field_name} 删除成功"
        }
    except Exception as e:
        print(f"删除字段失败: {e}")
        raise HTTPException(status_code=500, detail=f"删除字段失败: {str(e)}")


@router.post("/{table_name}/reorder-fields")
async def reorder_fields(table_name: str, data: Dict[str, Any]):
    """重新排序字段"""
    try:
        field_order = data.get("field_order", [])
        
        if not field_order:
            raise HTTPException(status_code=400, detail="字段顺序不能为空")
        
        # 更新配置文件中的字段顺序
        config = read_json_file(SCHEMA_FILE)
        if "tables" not in config:
            config["tables"] = {}
        
        if table_name not in config["tables"]:
            config["tables"][table_name] = {}
        
        table_config = config["tables"][table_name]
        table_config["field_order"] = field_order
        
        if write_json_file(SCHEMA_FILE, config):
            return {
                "status": "success",
                "message": "字段顺序更新成功"
            }
        else:
            raise HTTPException(status_code=500, detail="保存配置失败")
    except Exception as e:
        print(f"重新排序字段失败: {e}")
        raise HTTPException(status_code=500, detail=f"重新排序字段失败: {str(e)}")


@router.put("/{table_name}/rename")
async def rename_table(table_name: str, data: Dict[str, Any]):
    """修改表中文名称"""
    try:
        new_chinese_name = data.get("chinese_name")
        
        if not new_chinese_name:
            raise HTTPException(status_code=400, detail="表中文名称不能为空")
        
        # 更新配置文件
        config = read_json_file(SCHEMA_FILE)
        if "tables" not in config:
            config["tables"] = {}
        
        if table_name not in config["tables"]:
            config["tables"][table_name] = {}
        
        config["tables"][table_name]["chinese_name"] = new_chinese_name
        
        if write_json_file(SCHEMA_FILE, config):
            return {
                "status": "success",
                "message": f"表中文名称更新为: {new_chinese_name}"
            }
        else:
            raise HTTPException(status_code=500, detail="保存配置失败")
    except Exception as e:
        print(f"修改表名称失败: {e}")
        raise HTTPException(status_code=500, detail=f"修改表名称失败: {str(e)}")
