from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
import json
import os
from sqlalchemy import create_engine, text

router = APIRouter(prefix="/api/data", tags=["data"])

# 数据库连接
DATABASE_URL = "postgresql://taiping_user:taiping_password@localhost:5432/taiping_education"
engine = create_engine(DATABASE_URL)

# 配置文件路径
CONFIG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config')
SCHEMA_FILE = os.path.join(CONFIG_DIR, 'merged_schema_mappings.json')

# 默认字典关联配置
# 注意：只配置实际存在的字典表，code_field 必须是字典表的实际主键字段
DEFAULT_DICT_MAPPINGS = {
    '学历类型': {'table': 'education_dictionary', 'code_field': '学历类型', 'name_field': '类型名称', 'alias': '学历类型名称'},
    '学历': {'table': 'dict_education_dictionary', 'code_field': 'code', 'name_field': '学历', 'alias': '学历_name'},
    'position_level': {'table': 'dict_position', 'code_field': 'code', 'name_field': 'name', 'alias': 'position_level_name'},
    'personal_identity': {'table': 'dict_data_personal_identity', 'code_field': 'code', 'name_field': 'name', 'alias': 'personal_identity_name', 'link_field': 'personal_identity_code'},
}

# 检查字典表是否存在的缓存
dict_table_cache = {}

def check_dict_table_exists(table_name: str) -> bool:
    """检查字典表是否存在"""
    if table_name in dict_table_cache:
        return dict_table_cache[table_name]
    
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = :table_name
                )
            """), {"table_name": table_name})
            exists = result.scalar()
            dict_table_cache[table_name] = exists
            return exists
    except Exception as e:
        print(f"检查字典表存在性失败: {e}")
        return False


def read_json_file(file_path: str) -> Optional[Dict[str, Any]]:
    """读取JSON文件"""
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    except Exception as e:
        print(f"读取文件失败 {file_path}: {e}")
        return None


def get_table_schema_config(table_name: str) -> Dict[str, Any]:
    """获取表结构配置"""
    config = read_json_file(SCHEMA_FILE)
    if config and "tables" in config:
        return config["tables"].get(table_name, {})
    return {}


def get_dict_mappings_for_table(table_name: str, columns: List[str]) -> List[Dict[str, Any]]:
    """获取表的字典关联配置"""
    mappings = []
    
    # 使用默认字典关联配置
    for field_name in columns:
        if field_name in DEFAULT_DICT_MAPPINGS:
            dict_config = DEFAULT_DICT_MAPPINGS[field_name]
            # 检查字典表是否存在
            if check_dict_table_exists(dict_config['table']):
                mapping = {
                    'field': field_name,
                    'table': dict_config['table'],
                    'code_field': dict_config['code_field'],
                    'name_field': dict_config['name_field'],
                    'alias': dict_config['alias']
                }
                # 如果有指定关联字段，使用它
                if 'link_field' in dict_config:
                    mapping['link_field'] = dict_config['link_field']
                mappings.append(mapping)
    
    return mappings


@router.get("/schema/{table_name}")
async def get_table_schema(table_name: str):
    """获取表结构定义 - 从数据库读取实际结构"""
    try:
        # 首先尝试从配置文件读取
        config = read_json_file(SCHEMA_FILE)
        if config and "tables" in config:
            table_schema = config["tables"].get(table_name)
            if table_schema:
                return table_schema
        
        # 从数据库读取表结构
        with engine.connect() as conn:
            # 获取列信息
            result = conn.execute(text("""
                SELECT column_name, data_type, is_nullable, character_maximum_length
                FROM information_schema.columns
                WHERE table_name = :table_name
                ORDER BY ordinal_position
            """), {"table_name": table_name})
            
            fields = []
            for row in result:
                field_type = map_postgres_type_to_generic(row.data_type)
                field = {
                    "name": row.column_name,
                    "type": field_type,
                    "required": row.is_nullable == "NO"
                }
                if field_type == "VARCHAR" and row.character_maximum_length:
                    field["length"] = row.character_maximum_length
                fields.append(field)
            
            if fields:
                return {
                    "name": table_name,
                    "fields": fields
                }
        
        # 返回默认结构
        return {
            "name": table_name,
            "fields": [
                {"name": "id", "type": "INTEGER", "required": True},
                {"name": "name", "type": "VARCHAR", "length": 50},
                {"name": "created_at", "type": "DATETIME"}
            ]
        }
    except Exception as e:
        print(f"获取表结构失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取表结构失败: {str(e)}")


@router.get("/config/schema")
async def get_schema_mappings():
    """获取整个 schema mappings，包括所有表和字典表"""
    try:
        config = read_json_file(SCHEMA_FILE)
        if config:
            return config
        
        # 返回默认结构
        return {
            "tables": {},
            "dictionaries": {}
        }
    except Exception as e:
        print(f"获取 schema mappings 失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取 schema mappings 失败: {str(e)}")


def map_postgres_type_to_generic(pg_type: str) -> str:
    """将PostgreSQL类型映射为通用类型"""
    type_mapping = {
        "integer": "INTEGER",
        "bigint": "INTEGER",
        "smallint": "INTEGER",
        "numeric": "DECIMAL",
        "decimal": "DECIMAL",
        "real": "DECIMAL",
        "double precision": "DECIMAL",
        "character varying": "VARCHAR",
        "varchar": "VARCHAR",
        "character": "VARCHAR",
        "char": "VARCHAR",
        "text": "TEXT",
        "date": "DATE",
        "timestamp": "DATETIME",
        "timestamp without time zone": "DATETIME",
        "timestamp with time zone": "DATETIME",
        "boolean": "BOOLEAN",
        "bool": "BOOLEAN"
    }
    return type_mapping.get(pg_type.lower(), "VARCHAR")


@router.get("/{table_name}")
async def get_table_data(
    table_name: str,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=10000),
    filter: Optional[str] = Query(None),
    keyword: Optional[str] = Query(None)
):
    """获取表数据，支持搜索和筛选，自动关联字典表"""
    try:
        with engine.connect() as conn:
            # 获取表的所有列名
            columns_result = conn.execute(text("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = :table_name
                ORDER BY ordinal_position
            """), {"table_name": table_name})
            columns = [row.column_name for row in columns_result]

            # 获取字典关联配置
            dict_mappings = get_dict_mappings_for_table(table_name, columns)
            use_table_alias = len(dict_mappings) > 0

            # 构建搜索条件
            where_conditions = []
            params = {}

            # 处理关键词搜索
            if keyword:
                search_conditions = []
                for col in columns:
                    # 如果使用表别名，列名需要加 t. 前缀
                    col_ref = f"t.{col}" if use_table_alias else col
                    search_conditions.append(f"CAST({col_ref} AS TEXT) ILIKE :keyword")
                
                # 同时搜索字典中文名称
                for mapping in dict_mappings:
                    dict_alias = f"dict_{mapping['field']}"
                    search_conditions.append(f"CAST({dict_alias}.{mapping['name_field']} AS TEXT) ILIKE :keyword")
                
                where_conditions.append("(" + " OR ".join(search_conditions) + ")")
                params["keyword"] = f"%{keyword}%"

            # 处理筛选条件
            if filter:
                try:
                    filter_dict = json.loads(filter)
                    for field, value in filter_dict.items():
                        if field in columns and value:
                            param_name = f"filter_{field}"
                            # 如果使用表别名，列名需要加 t. 前缀
                            col_ref = f"t.{field}" if use_table_alias else field
                            where_conditions.append(f"CAST({col_ref} AS TEXT) ILIKE :{param_name}")
                            params[param_name] = f"%{value}%"
                except json.JSONDecodeError:
                    pass

            # 构建WHERE子句
            where_clause = ""
            if where_conditions:
                where_clause = "WHERE " + " AND ".join(where_conditions)

            # 获取总记录数
            # 如果使用表别名，COUNT查询也需要使用相同的表别名和JOIN
            if use_table_alias:
                count_join_clauses = []
                for mapping in dict_mappings:
                    dict_alias = f"dict_{mapping['field']}"
                    count_join_clauses.append(
                        f"LEFT JOIN {mapping['table']} {dict_alias} "
                        f"ON CAST(t.{mapping['field']} AS TEXT) = CAST({dict_alias}.{mapping['code_field']} AS TEXT)"
                    )
                count_sql = f"SELECT COUNT(*) FROM {table_name} t {' '.join(count_join_clauses)} {where_clause}"
            else:
                count_sql = f"SELECT COUNT(*) FROM {table_name} {where_clause}"
            count_result = conn.execute(text(count_sql), params)
            total = count_result.scalar()

            # 获取分页数据
            offset = (page - 1) * size
            params["size"] = size
            params["offset"] = offset

            # 构建查询SQL，关联字典表
            if use_table_alias:
                select_fields = [f"t.{col}" for col in columns]
                join_clauses = []

                for idx, mapping in enumerate(dict_mappings):
                    dict_alias = f"dict_{mapping['field']}"
                    select_fields.append(f"{dict_alias}.{mapping['name_field']} as {mapping['alias']}")
                    # 使用指定的关联字段，如果没有则使用原字段
                    link_field = mapping.get('link_field', mapping['field'])
                    join_clauses.append(
                        f"LEFT JOIN {mapping['table']} {dict_alias} "
                        f"ON CAST(t.{link_field} AS TEXT) = CAST({dict_alias}.{mapping['code_field']} AS TEXT)"
                    )

                data_sql = f"""
                    SELECT {', '.join(select_fields)}
                    FROM {table_name} t
                    {' '.join(join_clauses)}
                    {where_clause}
                    LIMIT :size OFFSET :offset
                """
            else:
                data_sql = f"SELECT * FROM {table_name} {where_clause} LIMIT :size OFFSET :offset"

            result = conn.execute(text(data_sql), params)

            # 转换结果为字典列表
            data = []
            for row in result:
                row_dict = {}
                for key, value in row._mapping.items():
                    # 处理日期时间类型
                    if hasattr(value, 'isoformat'):
                        row_dict[key] = value.isoformat()
                    else:
                        row_dict[key] = value
                data.append(row_dict)

            return {
                "data": data,
                "total": total,
                "page": page,
                "size": size
            }
    except Exception as e:
        print(f"获取数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取数据失败: {str(e)}")


@router.post("/export")
async def export_data(data: Dict[str, Any]):
    """导出数据到文件"""
    try:
        table_name = data.get('table_name', '')
        export_data_list = data.get('data', [])
        format_type = data.get('format', 'excel')
        filename = data.get('filename', f'export_{table_name}')
        export_path = data.get('path', 'D:\\exports')
        
        # 确保导出目录存在
        os.makedirs(export_path, exist_ok=True)
        
        if format_type == 'excel':
            # 导出为Excel
            file_path = os.path.join(export_path, f"{filename}.xlsx")
            
            # 使用pandas导出Excel
            import pandas as pd
            df = pd.DataFrame(export_data_list)
            df.to_excel(file_path, index=False, engine='openpyxl')
            
            return {
                "status": "success",
                "file_path": file_path,
                "format": "excel",
                "record_count": len(export_data_list)
            }
            
        elif format_type == 'pdf':
            # 导出为PDF
            file_path = os.path.join(export_path, f"{filename}.pdf")
            
            # 使用reportlab生成PDF
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import letter, landscape
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
            from reportlab.lib.styles import getSampleStyleSheet
            
            doc = SimpleDocTemplate(file_path, pagesize=landscape(letter))
            elements = []
            
            # 添加标题
            styles = getSampleStyleSheet()
            title = Paragraph(f"<b>{filename}</b>", styles['Heading1'])
            elements.append(title)
            
            # 准备表格数据
            if export_data_list:
                headers = list(export_data_list[0].keys())
                table_data = [headers]
                for row in export_data_list:
                    table_data.append([str(row.get(h, '')) for h in headers])
                
                table = Table(table_data)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                elements.append(table)
            
            doc.build(elements)
            
            return {
                "status": "success",
                "file_path": file_path,
                "format": "pdf",
                "record_count": len(export_data_list)
            }
            
        elif format_type == 'sql':
            # 导出为SQL
            file_path = os.path.join(export_path, f"{filename}.sql")
            
            with open(file_path, 'w', encoding='utf-8') as f:
                # 写入表结构（简化版）
                f.write(f"-- 导出表: {table_name}\n")
                f.write(f"-- 导出时间: {pd.Timestamp.now()}\n\n")
                
                # 生成INSERT语句
                for row in export_data_list:
                    columns = ', '.join([f'"{k}"' for k in row.keys()])
                    value_list = []
                    for v in row.values():
                        if v is None:
                            value_list.append('NULL')
                        else:
                            escaped = str(v).replace("'", "''")
                            value_list.append(f"'{escaped}'")
                    values = ', '.join(value_list)
                    f.write(f"INSERT INTO \"{table_name}\" ({columns}) VALUES ({values});\n")
            
            return {
                "status": "success",
                "file_path": file_path,
                "format": "sql",
                "record_count": len(export_data_list)
            }
        else:
            raise HTTPException(status_code=400, detail=f"不支持的导出格式: {format_type}")
            
    except Exception as e:
        print(f"导出失败: {e}")
        raise HTTPException(status_code=500, detail=f"导出失败: {str(e)}")


@router.post("/{table_name}")
async def create_record(table_name: str, data: Dict[str, Any]):
    """创建记录"""
    try:
        # 这里应该插入实际的数据库
        return {
            "status": "success",
            "message": "创建成功",
            "id": 1
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建失败: {str(e)}")


@router.put("/{table_name}/{record_id}")
async def update_record(table_name: str, record_id: int, data: Dict[str, Any]):
    """更新记录"""
    try:
        with engine.connect() as conn:
            # 构建 UPDATE 语句
            set_clauses = []
            params = {"record_id": record_id}
            
            for key, value in data.items():
                if key != "id":  # 不更新主键
                    set_clauses.append(f"{key} = :{key}")
                    params[key] = value
            
            if not set_clauses:
                return {
                    "status": "success",
                    "message": "没有需要更新的字段"
                }
            
            update_sql = f"UPDATE {table_name} SET {', '.join(set_clauses)} WHERE id = :record_id"
            result = conn.execute(text(update_sql), params)
            conn.commit()
            
            if result.rowcount > 0:
                return {
                    "status": "success",
                    "message": "更新成功",
                    "updated_rows": result.rowcount
                }
            else:
                raise HTTPException(status_code=404, detail="记录不存在")
    except Exception as e:
        print(f"更新失败: {e}")
        raise HTTPException(status_code=500, detail=f"更新失败: {str(e)}")


@router.delete("/{table_name}/{record_id}")
async def delete_record(table_name: str, record_id: int):
    """删除记录"""
    try:
        with engine.connect() as conn:
            # 执行删除操作
            delete_sql = f"DELETE FROM {table_name} WHERE id = :record_id"
            result = conn.execute(text(delete_sql), {"record_id": record_id})
            conn.commit()
            
            if result.rowcount > 0:
                return {
                    "status": "success",
                    "message": "删除成功",
                    "deleted_count": result.rowcount
                }
            else:
                raise HTTPException(status_code=404, detail="记录不存在")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")


@router.get("/ui-components/{table_name}")
async def get_ui_components(table_name: str):
    """获取UI组件配置"""
    try:
        # 这里应该从配置文件读取
        return {
            "actions": [
                {
                    "key": "smartFill",
                    "label": "智能填充",
                    "icon": "MagicStick",
                    "type": "primary",
                    "requireSelection": False
                },
                {
                    "key": "batchTag",
                    "label": "批量打标签",
                    "icon": "CollectionTag",
                    "type": "default",
                    "requireSelection": True
                },
                {
                    "key": "generateReport",
                    "label": "生成报表",
                    "icon": "Document",
                    "type": "success",
                    "requireSelection": False
                }
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取UI配置失败: {str(e)}")
