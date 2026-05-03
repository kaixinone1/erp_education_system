from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import psycopg2
import json
import os
from functools import lru_cache

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

def load_dict_mappings():
    config_file = os.path.join(os.path.dirname(__file__), '..', 'config', 'dict_mappings.json')
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

def load_table_relations():
    config_file = os.path.join(os.path.dirname(__file__), '..', 'config', 'table_relations.json')
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

class DictCache:
    _cache = {}
    _loaded = False

    @classmethod
    def load_all_dicts(cls, conn):
        if cls._loaded and cls._cache:
            return cls._cache

        dict_mappings = load_dict_mappings()
        cursor = conn.cursor()
        cache = {}

        for table_name, fields in dict_mappings.items():
            for field_label, config in fields.items():
                dict_table = config.get("table")
                code_field = config.get("code", "id")
                name_field = config.get("name")

                if not dict_table or not name_field:
                    continue

                try:
                    cursor.execute(f'SELECT {code_field}, {name_field} FROM {dict_table}')
                    rows = cursor.fetchall()
                    cache_key = f"{table_name}.{field_label}"
                    cache[cache_key] = {str(row[0]): row[1] for row in rows}
                except Exception as e:
                    print(f"加载字典表{dict_table}失败: {e}")

        cursor.close()
        cls._cache = cache
        cls._loaded = True
        return cache

    @classmethod
    def get_translation(cls, table_name: str, field_label: str, code_value: Any) -> Any:
        if not cls._loaded:
            conn = get_db_connection()
            cls.load_all_dicts(conn)
            conn.close()

        cache_key = f"{table_name}.{field_label}"
        if cache_key in cls._cache and code_value is not None:
            return cls._cache[cache_key].get(str(code_value), code_value)
        return code_value

    @classmethod
    def clear(cls):
        cls._cache = {}
        cls._loaded = False

class TableListRequest(BaseModel):
    pass

class TableFieldsRequest(BaseModel):
    table_name: str

class AggregateQueryRequest(BaseModel):
    tables: List[Dict[str, Any]]
    group_by: Optional[str] = None
    tags: Optional[List[str]] = None
    filters: Optional[List[Dict[str, Any]]] = None
    page: Optional[int] = 1
    page_size: Optional[int] = 0

class ExportRequest(BaseModel):
    data: List[Dict[str, Any]]
    filename: str

class SaveQueryConfigRequest(BaseModel):
    name: str
    tables: List[Dict[str, Any]]
    tags: Optional[List[str]] = None
    target_table: Optional[str] = None

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

@router.post("/dict-values")
def get_dict_values(req: dict):
    """获取字典字段的可选值列表"""
    try:
        table_name = req.get("table_name")
        field_name = req.get("field_name")

        if not table_name or not field_name:
            return {"status": "success", "values": []}

        # 加载 merged_schema_mappings.json 获取字段的字典关联配置
        schema_file = os.path.join(os.path.dirname(__file__), '..', 'config', 'merged_schema_mappings.json')
        try:
            with open(schema_file, 'r', encoding='utf-8') as f:
                schema_data = json.load(f)
                table_fields = schema_data.get('tables', {}).get(table_name, {}).get('fields', [])
                for field in table_fields:
                    target = field.get('targetField') or field.get('english_name')
                    if target == field_name:
                        relation_table = field.get('relation_table')
                        if relation_table:
                            # 连接数据库获取字典值
                            conn = get_db_connection()
                            cursor = conn.cursor()
                            # 获取字典表的第一个字段作为code，第二个作为name
                            cursor.execute(f"""
                                SELECT column_name FROM information_schema.columns
                                WHERE table_name = %s AND table_schema = 'public'
                                AND column_name NOT IN ('created_at', 'updated_at')
                                ORDER BY ordinal_position LIMIT 2
                            """, (relation_table,))
                            cols = cursor.fetchall()
                            if len(cols) >= 2:
                                code_col = cols[0][0]
                                name_col = cols[1][0]
                                cursor.execute(f'SELECT {code_col}, {name_col} FROM {relation_table}')
                                values = [{"value": row[0], "label": row[1]} for row in cursor.fetchall()]
                                cursor.close()
                                conn.close()
                                return {"status": "success", "values": values}
                            cursor.close()
                            conn.close()
        except Exception as e:
            print(f"加载字典配置失败: {e}")

        return {"status": "success", "values": []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/relations")
def get_table_relations():
    try:
        relations = load_table_relations()
        return {"status": "success", "relations": relations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/fields")
def get_table_fields(req: TableFieldsRequest):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT c.column_name, c.data_type, c.ordinal_position
            FROM information_schema.columns c
            WHERE c.table_name = %s
            AND c.table_schema = 'public'
            ORDER BY c.ordinal_position
        """, (req.table_name,))

        # 加载 merged_schema_mappings.json 获取中文字段名映射
        schema_file = os.path.join(os.path.dirname(__file__), '..', 'config', 'merged_schema_mappings.json')
        print(f"[DEBUG] schema_file: {schema_file}, exists: {os.path.exists(schema_file)}")
        chinese_labels = {}
        table_fields_config = []
        try:
            with open(schema_file, 'r', encoding='utf-8') as f:
                schema_data = json.load(f)
                table_fields = schema_data.get('tables', {}).get(req.table_name, {}).get('fields', [])
                table_fields_config = table_fields
                print(f"[DEBUG] table_fields count: {len(table_fields)}")
                for field in table_fields:
                    english_name = field.get('english_name') or field.get('targetField', '')
                    chinese_name = field.get('sourceField', '')
                    if english_name and chinese_name:
                        chinese_labels[english_name] = chinese_name
                print(f"[DEBUG] chinese_labels: {chinese_labels}")
        except Exception as e:
            print(f"加载 merged_schema_mappings.json 失败: {e}")

        fields = []
        for row in cursor.fetchall():
            column_name = row[0]
            chinese_name = chinese_labels.get(column_name, column_name)
            has_dict = any(
                field.get('relation_table', '').startswith('dict_')
                for field in table_fields_config
                if (field.get('english_name') or field.get('targetField', '')) == column_name
            )

            fields.append({
                "name": column_name,
                "label": chinese_name,
                "type": row[1],
                "has_dict": has_dict
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

        page = req.page or 1
        page_size = req.page_size or 1000
        offset = (page - 1) * page_size

        if len(req.tables) == 1:
            table_info = req.tables[0]
            table_name = table_info.get("table_name")
            fields = table_info.get("fields", [])

            if not fields:
                return {"status": "success", "data": [], "total": 0, "page": page, "page_size": page_size}

            select_fields = ", ".join([f'"{f["name"]}"' for f in fields])

            where_clauses = []
            params = []

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

            # 处理字段过滤条件
            if req.filters:
                for f in req.filters:
                    field_name = f.get("field")
                    operator = f.get("operator", "=")
                    field_value = f.get("value")
                    field_values = f.get("values")
                    if field_name:
                        if field_values and len(field_values) > 0:
                            placeholders = ','.join(['%s'] * len(field_values))
                            where_clauses.append(f'"{field_name}" IN ({placeholders})')
                            params.extend(field_values)
                        elif field_value:
                            where_clauses.append(f'"{field_name}" {operator} %s')
                            params.append(field_value)

            where_sql = ""
            if where_clauses:
                where_sql = " WHERE " + " AND ".join(where_clauses)

            # 统计总数
            count_query = f'SELECT COUNT(*) FROM "{table_name}"{where_sql}'
            cursor.execute(count_query, params)
            total = cursor.fetchone()[0]

            # 分页查询（page_size=0表示不限制）
            if page_size > 0:
                query = f'SELECT {select_fields} FROM "{table_name}"{where_sql} LIMIT %s OFFSET %s'
                cursor.execute(query, params + [page_size, offset])
            else:
                query = f'SELECT {select_fields} FROM "{table_name}"{where_sql}'
                cursor.execute(query, params)
            rows = cursor.fetchall()

            results = []
            for row in rows:
                result_row = {}
                for i, field in enumerate(fields):
                    chinese_label = field.get("label", field["name"])
                    value = row[i]
                    # 字典翻译
                    if field.get("has_dict"):
                        value = DictCache.get_translation(table_name, field["name"], value)
                    result_row[chinese_label] = value
                results.append(result_row)
        else:
            first_table = req.tables[0]
            first_table_name = first_table.get("table_name")
            first_fields = first_table.get("fields", [])

            if not first_fields:
                return {"status": "success", "data": [], "total": 0, "page": page, "page_size": page_size}

            select_parts = []
            join_parts = []
            where_clauses = []
            params = []

            for i, field in enumerate(first_fields):
                chinese_label = field.get("label", field["name"])
                select_parts.append(f'"{first_table_name}"."{field["name"]}" AS "{chinese_label}"')

            for idx, table_info in enumerate(req.tables[1:], 1):
                table_name = table_info.get("table_name")
                table_fields = table_info.get("fields", [])
                table_alias = f"t{idx}"

                join_parts.append(f'LEFT JOIN "{table_name}" {table_alias} ON "{first_table_name}".id_card = {table_alias}.id_card')

                for i, field in enumerate(table_fields):
                    chinese_label = field.get("label", field["name"])
                    select_parts.append(f'{table_alias}."{field["name"]}" AS "{chinese_label}"')

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

            # 处理多表查询的字段过滤条件
            if req.filters:
                for f in req.filters:
                    field_name = f.get("field")
                    field_table = f.get("table")
                    field_values = f.get("values")
                    if field_name and field_values and len(field_values) > 0:
                        # 找到该表对应的别名
                        table_alias = None
                        if field_table == first_table_name:
                            table_alias = first_table_name
                        else:
                            for idx, table_info in enumerate(req.tables[1:], 1):
                                if table_info.get("table_name") == field_table:
                                    table_alias = f"t{idx}"
                                    break
                        if table_alias:
                            placeholders = ','.join(['%s'] * len(field_values))
                            # 将值转换为字符串，因为字段可能是VARCHAR类型
                            str_values = [str(v) for v in field_values]
                            if table_alias == first_table_name:
                                where_clauses.append(f'"{table_alias}"."{field_name}" IN ({placeholders})')
                            else:
                                where_clauses.append(f'{table_alias}."{field_name}" IN ({placeholders})')
                            params.extend(str_values)

            where_sql = ""
            if where_clauses:
                where_sql = " WHERE " + " AND ".join(where_clauses)

            # 统计总数
            count_query = f'SELECT COUNT(*) FROM "{first_table_name}" {" ".join(join_parts)}{where_sql}'
            cursor.execute(count_query, params)
            total = cursor.fetchone()[0]

            # 分页查询（page_size=0表示不限制）
            if page_size > 0:
                query = f"""
                    SELECT {', '.join(select_parts)}
                    FROM "{first_table_name}"
                    {(' ').join(join_parts)}
                    {where_sql}
                    LIMIT %s OFFSET %s
                """
                cursor.execute(query, params + [page_size, offset])
            else:
                query = f"""
                    SELECT {', '.join(select_parts)}
                    FROM "{first_table_name}"
                    {(' ').join(join_parts)}
                    {where_sql}
                """
                cursor.execute(query, params)
            rows = cursor.fetchall()

            all_field_labels = []
            for i, field in enumerate(first_fields):
                all_field_labels.append(field.get("label", field["name"]))
            for idx, table_info in enumerate(req.tables[1:], 1):
                for i, field in enumerate(table_info.get("fields", [])):
                    all_field_labels.append(field.get("label", field["name"]))

            results = []
            for row in rows:
                result_row = {}
                for i, label in enumerate(all_field_labels):
                    value = row[i]
                    # 找到对应的表和字段进行字典翻译
                    result_row[label] = value
                results.append(result_row)

            # 多表查询字典翻译
            schema_file = os.path.join(os.path.dirname(__file__), '..', 'config', 'merged_schema_mappings.json')
            try:
                with open(schema_file, 'r', encoding='utf-8') as f:
                    schema_data = json.load(f)

                for result_row in results:
                    for label, value in result_row.items():
                        if value is not None:
                            # 查找该字段的字典配置
                            for table_info in req.tables:
                                table_name = table_info.get("table_name")
                                table_fields = table_info.get("fields", [])
                                for field in table_fields:
                                    if field.get("label") == label:
                                        table_fields_config = schema_data.get('tables', {}).get(table_name, {}).get('fields', [])
                                        for field_config in table_fields_config:
                                            if field_config.get('english_name') == field.get('name') or field_config.get('targetField') == field.get('name'):
                                                if field_config.get('relation_type') == 'to_dict' and field_config.get('relation_table'):
                                                    dict_table = field_config['relation_table']
                                                    dict_display_field = field_config.get('relation_display_field', 'category')
                                                    cursor2 = conn.cursor()
                                                    cursor2.execute(f'SELECT id, {dict_display_field} FROM {dict_table} WHERE id = %s', (value,))
                                                    dict_row = cursor2.fetchone()
                                                    if dict_row:
                                                        result_row[label] = dict_row[1]
                                                    cursor2.close()
            except Exception as e:
                print(f"多表查询字典翻译失败: {e}")

        cursor.close()
        conn.close()

        return {"status": "success", "data": results, "total": total, "page": page, "page_size": page_size}
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

@router.post("/save-config")
def save_query_config(req: SaveQueryConfigRequest):
    """保存查询配置"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO query_configs (name, config, tags, target_table, created_at, updated_at)
            VALUES (%s, %s, %s, %s, NOW(), NOW())
            RETURNING id
        """, (req.name, json.dumps(req.tables), json.dumps(req.tags), req.target_table))

        config_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()

        return {"status": "success", "id": config_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/configs")
def get_query_configs():
    """获取所有查询配置"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, name, config, tags, target_table, created_at, updated_at
            FROM query_configs
            ORDER BY updated_at DESC
        """)

        configs = []
        for row in cursor.fetchall():
            configs.append({
                "id": row[0],
                "name": row[1],
                "config": row[2],
                "tags": row[3],
                "target_table": row[4],
                "created_at": row[5].isoformat() if row[5] else None,
                "updated_at": row[6].isoformat() if row[6] else None
            })

        cursor.close()
        conn.close()

        return {"status": "success", "configs": configs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/configs/{config_id}")
def delete_query_config(config_id: int):
    """删除查询配置"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM query_configs WHERE id = %s", (config_id,))
        conn.commit()
        cursor.close()
        conn.close()

        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))