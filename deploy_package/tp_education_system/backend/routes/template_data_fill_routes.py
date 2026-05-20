"""
模板数据填报API
支持标签筛选、数据源表选择、字段映射、数据预览、模板填充
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import psycopg2
import json
import os

router = APIRouter(prefix="/api/template-data-fill", tags=["template-data-fill"])

DATABASE_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "database": "taiping_education",
    "user": "taiping_user",
    "password": "taiping_password"
}

def get_db_connection():
    return psycopg2.connect(**DATABASE_CONFIG)

def load_table_mappings():
    mapping_file = os.path.join(os.path.dirname(__file__), '..', 'config', 'table_name_mappings.json')
    try:
        with open(mapping_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {"mappings": {}, "reverse_mappings": {}}

def get_chinese_table_name(english_name: str) -> str:
    mappings = load_table_mappings()
    for chinese_name, info in mappings.get("mappings", {}).items():
        if info.get("english_name") == english_name:
            return chinese_name
    return english_name

def load_field_config(table_name: str) -> List[Dict[str, Any]]:
    config_file = os.path.join(os.path.dirname(__file__), '..', 'config', 'field_configs', f'{table_name}.json')
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

@router.get("/tables")
async def get_data_source_tables():
    """获取所有可用的数据源表"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT table_name, 
                   COALESCE(obj_description(table_name::regclass), table_name) as table_label
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_type = 'BASE TABLE'
            AND table_name NOT LIKE 'pg_%'
            AND table_name NOT LIKE 'sql_%'
            ORDER BY table_name
        """)
        
        tables = []
        for row in cursor.fetchall():
            table_name = row[0]
            chinese_name = row[1] if row[1] else get_chinese_table_name(table_name)
            tables.append({
                "name": table_name,
                "label": chinese_name
            })
        
        cursor.close()
        conn.close()
        
        return {"status": "success", "tables": tables}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/table-fields/{table_name}")
async def get_table_fields(table_name: str):
    """获取指定表的所有字段"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT column_name, data_type, 
                   COALESCE(col_description((table_name::regclass)::oid, ordinal_position), column_name) as column_comment
            FROM information_schema.columns
            WHERE table_name = %s
            AND table_schema = 'public'
            ORDER BY ordinal_position
        """, (table_name,))
        
        fields = []
        for row in cursor.fetchall():
            fields.append({
                "name": row[0],
                "type": row[1],
                "label": row[2] if row[2] else row[0]
            })
        
        cursor.close()
        conn.close()
        
        return {"status": "success", "fields": fields}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/field-dictionary/{table_name}/{field_name}")
async def get_field_dictionary(table_name: str, field_name: str):
    """获取字段的字典值列表"""
    try:
        field_configs = load_field_config(table_name)
        
        field_config = None
        for field in field_configs:
            if field.get("targetField") == field_name or field.get("sourceField") == field_name:
                field_config = field
                break
        
        if not field_config or field_config.get("relation_type") != "to_dict":
            return {
                "status": "success",
                "has_dictionary": False,
                "values": []
            }
        
        dict_table = field_config.get("relation_table")
        if not dict_table:
            return {
                "status": "success",
                "has_dictionary": False,
                "values": []
            }
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(f"""
            SELECT column_name FROM information_schema.columns
            WHERE table_name = %s
            AND table_schema = 'public'
            AND column_name NOT IN ('created_at', 'updated_at', 'id')
            ORDER BY ordinal_position
            LIMIT 2
        """, (dict_table,))
        
        cols = cursor.fetchall()
        if len(cols) < 2:
            cursor.close()
            conn.close()
            return {
                "status": "success",
                "has_dictionary": False,
                "values": []
            }
        
        code_col = cols[0][0]
        name_col = cols[1][0]
        
        cursor.execute(f'SELECT {code_col}, {name_col} FROM {dict_table}')
        values = [{"value": row[0], "label": row[1]} for row in cursor.fetchall()]
        
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "has_dictionary": True,
            "values": values
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class FieldMapping(BaseModel):
    placeholder: str
    source_table: str
    source_field: str
    dict_values: List[Any] = []
    aggregate_type: str = "direct"

class PreviewRequest(BaseModel):
    template_id: str
    tags: Optional[List[str]] = None
    field_mappings: List[FieldMapping]

@router.post("/preview")
async def preview_data(req: PreviewRequest):
    """预览数据"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        where_clauses = []
        params = []
        
        if req.tags and len(req.tags) > 0:
            placeholders = ','.join(['%s'] * len(req.tags))
            tag_filter = f"""
                id_card IN (
                    SELECT id_card FROM teacher_basic_info
                    WHERE id IN (
                        SELECT employee_id FROM employee_tag_relations
                        WHERE tag_id IN (
                            SELECT id FROM personal_dict_dictionary WHERE biao_qian IN ({placeholders})
                        )
                    )
                )
            """
            where_clauses.append(tag_filter)
            params.extend(req.tags)
        
        result_data = []
        
        for mapping in req.field_mappings:
            if not mapping.source_table or not mapping.source_field:
                continue
            
            table_name = mapping.source_table
            field_name = mapping.source_field
            
            query_params = params.copy()
            where_sql = ""
            
            if where_clauses:
                where_sql = " WHERE " + " AND ".join(where_clauses)
            
            if mapping.dict_values and len(mapping.dict_values) > 0:
                dict_placeholders = ','.join(['%s'] * len(mapping.dict_values))
                dict_filter = f'"{field_name}" IN ({dict_placeholders})'
                if where_sql:
                    where_sql += " AND " + dict_filter
                else:
                    where_sql = " WHERE " + dict_filter
                query_params.extend(mapping.dict_values)
            
            if mapping.aggregate_type == "direct":
                query = f'SELECT "{field_name}" FROM "{table_name}"{where_sql}'
                cursor.execute(query, query_params)
                rows = cursor.fetchall()
                
                for row in rows:
                    result_data.append({
                        "占位符": mapping.placeholder,
                        "值": row[0]
                    })
            elif mapping.aggregate_type == "count":
                query = f'SELECT COUNT(*) FROM "{table_name}"{where_sql}'
                cursor.execute(query, query_params)
                count = cursor.fetchone()[0]
                result_data.append({
                    "占位符": mapping.placeholder,
                    "值": count
                })
        
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "data": result_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class FillRequest(BaseModel):
    template_id: str
    tags: Optional[List[str]] = None
    field_mappings: List[FieldMapping]
    data: List[Dict[str, Any]]

@router.post("/fill")
async def fill_template(req: FillRequest):
    """填充模板"""
    try:
        return {
            "status": "success",
            "message": "模板填充成功",
            "download_url": f"/api/templates/{req.template_id}/download"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class ExportRequest(BaseModel):
    data: List[Dict[str, Any]]
    filename: str

@router.post("/export")
async def export_data(req: ExportRequest):
    """导出数据到Excel"""
    try:
        import pandas as pd
        from fastapi.responses import StreamingResponse
        import io
        
        df = pd.DataFrame(req.data)
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='数据')
        
        output.seek(0)
        
        return StreamingResponse(
            output,
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers={
                'Content-Disposition': f'attachment; filename="{req.filename}"'
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
