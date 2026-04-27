from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import psycopg2
import json
import os

router = APIRouter(prefix="/api/aggregate-query", tags=["聚合查询"])

def get_db_connection():
    return psycopg2.connect(
        host='localhost',
        port='5432',
        database='taiping_education',
        user='taiping_user',
        password='taiping_password'
    )

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

def load_field_mappings():
    """从 field_mapping_config.json 加载字段映射"""
    config_file = os.path.join(os.path.dirname(__file__), '..', 'config', 'field_mapping_config.json')
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

def get_field_label_from_config(table_name: str, field_name: str) -> str:
    """从配置文件获取字段的中文标签 - 尝试关键字匹配"""
    import glob
    
    # 关键字匹配表：英文字段名 -> 中文名
    keyword_map = {
        'teacher_basic_info': {
            'name': '姓名',
            'id_card': '身份证号码',
            'gender': '性别',
            'birth_date': '出生日期',
            'ethnicity': '民族',
            'native_place': '籍贯',
            'contact_phone': '联系电话',
            'work_start_date': '参加工作时间',
            'entry_date': '进入本单位日期',
            'employment_status': '任职状态',
            'archive_birth_date': '档案出生日期',
        },
        'teacher_personal_identity': {
            'name': '姓名',
            'id_card': '身份证号码',
            'ge_ren_shen_fen': '个人身份',
        }
    }
    
    if table_name in keyword_map and field_name in keyword_map[table_name]:
        return keyword_map[table_name][field_name]
    
    return None

# 字典表关联配置：表名.字段名 -> 字典表名
DICT_MAPPINGS = {
    "teacher_personal_identity.个人身份": "dict_personal_identity_dictionary",
    "teacher_basic_info.民族": "dict_nation_dictionary",
    "teacher_basic_info.婚姻状况": "dict_marital_status_dictionary",
    "teacher_basic_info.政治面貌": "dict_politics_status_dictionary",
}

def load_dict_values():
    """加载所有字典表的翻译映射"""
    dict_values = {}
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 加载个人身份字典 - 使用英文字段名
        cursor.execute("SELECT id, ge_ren_shen_fen FROM dict_personal_identity_dictionary")
        dict_values["dict_personal_identity_dictionary"] = {str(row[0]): row[1] for row in cursor.fetchall()}
        
        # 加载民族字典
        cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'dict_nation_dictionary'")
        nation_cols = [r[0] for r in cursor.fetchall()]
        if '民族' in nation_cols:
            cursor.execute("SELECT id, 民族 FROM dict_nation_dictionary")
            dict_values["dict_nation_dictionary"] = {str(row[0]): row[1] for row in cursor.fetchall()}
        
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"加载字典表失败: {e}")
    
    print(f"load_dict_values返回: {dict_values}")
    return dict_values

def translate_values(data: List[Dict], tables: List[Dict]) -> List[Dict]:
    """翻译查询结果中的代码值"""
    dict_values = load_dict_values()
    print(f"字典值加载结果: {dict_values}")
    
    # 构建字段到字典的映射 - 用中文字段名作为key
    field_dict_map = {}
    for table_info in tables:
        table_name = table_info.get("table_name", "")  # 英文表名
        fields = table_info.get("fields", [])
        for field in fields:
            field_label = field.get("label", "")  # 中文字段名
            key = f"{table_name}.{field_label}"  # 英文表名.中文字段名
            print(f"检查映射: {key} -> {DICT_MAPPINGS.get(key)}")
            if key in DICT_MAPPINGS:
                field_dict_map[field_label] = DICT_MAPPINGS[key]
    
    print(f"字段字典映射: {field_dict_map}")
    
    # 翻译每个记录
    results = []
    for record in data:
        translated = {}
        for key, value in record.items():
            if key in field_dict_map and value is not None:
                dict_table = field_dict_map[key]
                if dict_table in dict_values:
                    translated[key] = dict_values[dict_table].get(str(value), value)
                else:
                    translated[key] = value
            else:
                translated[key] = value
        results.append(translated)
    
    return results

class TableListRequest(BaseModel):
    pass

class TableFieldsRequest(BaseModel):
    table_name: str

class AggregateQueryRequest(BaseModel):
    tables: List[Dict[str, Any]]
    group_by: Optional[str] = None
    tags: Optional[List[str]] = None

class ExportRequest(BaseModel):
    data: List[Dict[str, Any]]
    filename: str

@router.get("/tables")
def get_tables():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT t.table_name, obj_description(t.table_name::regclass) as table_comment
            FROM information_schema.tables t
            WHERE t.table_schema = 'public' 
            AND t.table_type = 'BASE TABLE'
            AND t.table_name NOT LIKE 'pg_%'
            AND t.table_name NOT LIKE 'sql_%'
            ORDER BY t.table_name
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

@router.post("/fields")
def get_table_fields(req: TableFieldsRequest):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 从数据库注释获取字段中文名
        cursor.execute("""
            SELECT c.column_name, c.data_type, c.ordinal_position,
                   col_description(c.table_name::regclass, c.ordinal_position) as column_comment
            FROM information_schema.columns c
            WHERE c.table_name = %s 
            AND c.table_schema = 'public'
            ORDER BY c.ordinal_position
        """, (req.table_name,))
        
        fields = []
        for row in cursor.fetchall():
            column_name = row[0]
            column_comment = row[3]  # 数据库注释
            # 优先用配置文件，其次用数据库注释，最后用英文
            chinese_name = get_field_label_from_config(req.table_name, column_name)
            if not chinese_name:
                chinese_name = column_comment if column_comment else column_name
            fields.append({
                "name": column_name,
                "label": chinese_name,
                "type": row[1]
            })
        
        cursor.close()
        conn.close()
        
        return {"status": "success", "fields": fields}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/query")
def aggregate_query(req: AggregateQueryRequest):
    """执行聚合查询 - 支持多表关联和字典翻译"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if len(req.tables) == 1:
            # 单表查询
            table_info = req.tables[0]
            table_name = table_info.get("table_name")
            fields = table_info.get("fields", [])
            
            if not fields:
                return {"status": "success", "data": []}
            
            field_config_map = get_field_mapping_from_config(table_name)
            select_fields = ", ".join([f'"{f["name"]}"' for f in fields])
            
            where_clauses = []
            params = []
            
            # 标签筛选
            if req.tags:
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
            
            where_sql = ""
            if where_clauses:
                where_sql = " WHERE " + " AND ".join(where_clauses)
            
            query = f'SELECT {select_fields} FROM "{table_name}"{where_sql}'
            print(f"单表查询: {query}")
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            results = []
            for row in rows:
                result_row = {}
                for i, field in enumerate(fields):
                    # 直接使用前端传来的label
                    chinese_label = field.get("label", field["name"])
                    result_row[chinese_label] = row[i]
                results.append(result_row)
            
            # 翻译字典值
            results = translate_values(results, req.tables)
        else:
            # 多表关联查询 - 通过id_card关联
            first_table = req.tables[0]
            first_table_name = first_table.get("table_name")
            first_fields = first_table.get("fields", [])
            
            if not first_fields:
                return {"status": "success", "data": []}
            
            # 构建主查询
            select_parts = []
            join_parts = []
            where_clauses = []
            params = []
            
            # 主表字段 - 直接使用前端传来的label
            for i, field in enumerate(first_fields):
                chinese_label = field.get("label", field["name"])
                select_parts.append(f'"{first_table_name}"."{field["name"]}" AS "{chinese_label}"')
            
            # 关联表
            for idx, table_info in enumerate(req.tables[1:], 1):
                table_name = table_info.get("table_name")
                table_fields = table_info.get("fields", [])
                table_alias = f"t{idx}"
                
                # 通过id_card关联
                join_parts.append(f'LEFT JOIN "{table_name}" {table_alias} ON "{first_table_name}".id_card = {table_alias}.id_card')
                
                # 关联表字段 - 直接使用前端传来的label
                for i, field in enumerate(table_fields):
                    chinese_label = field.get("label", field["name"])
                    select_parts.append(f'{table_alias}."{field["name"]}" AS "{chinese_label}"')
            
            # 标签筛选
            if req.tags:
                placeholders = ','.join(['%s'] * len(req.tags))
                tag_filter = f"""
                    "{first_table_name}".id_card IN (
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
            
            where_sql = ""
            if where_clauses:
                where_sql = " WHERE " + " AND ".join(where_clauses)
            
            query = f"""
                SELECT {', '.join(select_parts)}
                FROM "{first_table_name}"
                {(' ').join(join_parts)}
                {where_sql}
            """
            print(f"多表关联查询: {query}")
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            # 构建所有字段的中文名列表 - 直接使用前端传来的label
            all_field_labels = []
            # 主表字段
            for i, field in enumerate(first_fields):
                chinese_label = field.get("label", field["name"])
                all_field_labels.append(chinese_label)
            # 关联表字段
            for idx, table_info in enumerate(req.tables[1:], 1):
                table_fields = table_info.get("fields", [])
                for i, field in enumerate(table_fields):
                    chinese_label = field.get("label", field["name"])
                    all_field_labels.append(chinese_label)
            
            results = []
            for row in rows:
                result_row = {}
                for i, label in enumerate(all_field_labels):
                    result_row[label] = row[i]
                results.append(result_row)
            
            # 翻译字典值
            results = translate_values(results, req.tables)
        
        cursor.close()
        conn.close()
        
        return {"status": "success", "data": results}
    except Exception as e:
        import traceback
        print(f"查询失败: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tags")
def get_tags():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, biao_qian 
            FROM personal_dict_dictionary 
            WHERE biao_qian IS NOT NULL 
            ORDER BY biao_qian
        """)
        tags = [{"id": row[0], "name": row[1]} for row in cursor.fetchall()]
        
        cursor.close()
        conn.close()
        
        return {"status": "success", "tags": tags}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/export")
def export_query_data(req: ExportRequest):
    try:
        import pandas as pd
        from fastapi.responses import FileResponse
        import tempfile
        
        df = pd.DataFrame(req.data)
        
        if "_table" in df.columns:
            df = df.drop(columns=["_table"])
        
        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, f"{req.filename}.xlsx")
        
        df.to_excel(file_path, index=False)
        
        return FileResponse(
            file_path, 
            filename=f"{req.filename}.xlsx",
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
