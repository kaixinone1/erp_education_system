"""
模板数据填报API
提供数据源表和字段信息，用于字段映射配置的下拉选择
"""
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
import json
import os

router = APIRouter(prefix="/api/template-data-fill", tags=["模板数据填报"])

CONFIG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config')
FIELD_CONFIGS_DIR = os.path.join(CONFIG_DIR, 'field_configs')
MAPPINGS_FILE = os.path.join(CONFIG_DIR, 'table_name_mappings.json')


def _load_table_mappings() -> Dict[str, str]:
    en_to_cn = {}
    if not os.path.exists(MAPPINGS_FILE):
        return en_to_cn
    with open(MAPPINGS_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    for chinese_name, info in data.get('mappings', {}).items():
        english_name = info.get('english_name', '')
        if english_name:
            en_to_cn[english_name] = chinese_name
    return en_to_cn


def _load_field_configs_index() -> Dict[str, Dict[str, Any]]:
    index = {}
    if not os.path.exists(FIELD_CONFIGS_DIR):
        return index
    for filename in os.listdir(FIELD_CONFIGS_DIR):
        if not filename.endswith('.json'):
            continue
        filepath = os.path.join(FIELD_CONFIGS_DIR, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            table_name = data.get('table_name', '')
            if table_name:
                index[table_name] = {
                    'config_name': data.get('config_name', ''),
                    'table_type': data.get('table_type', 'master'),
                    'field_configs': data.get('field_configs', [])
                }
        except Exception:
            continue
    return index


@router.get("/tables")
async def get_data_source_tables():
    try:
        en_to_cn = _load_table_mappings()
        field_index = _load_field_configs_index()

        tables = []
        for english_name, chinese_name in en_to_cn.items():
            tables.append({
                "name": english_name,
                "label": chinese_name
            })

        for table_name, config in field_index.items():
            if table_name not in en_to_cn:
                tables.append({
                    "name": table_name,
                    "label": config.get('config_name', table_name)
                })

        return {"status": "success", "tables": tables}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/table-fields/{table_name}")
async def get_table_fields(table_name: str):
    try:
        field_index = _load_field_configs_index()

        config = field_index.get(table_name)
        if not config:
            return {
                "status": "success",
                "fields": [],
                "is_dict_table": False,
                "dict_table_config": None
            }

        fields = []
        for fc in config.get('field_configs', []):
            source_field = fc.get('sourceField', '')
            target_field = fc.get('targetField', '')
            fields.append({
                "name": target_field,
                "label": source_field,
                "type": fc.get('dataType', 'VARCHAR')
            })

        is_dict_table = config.get('table_type') == 'dictionary'
        dict_table_config = None
        if is_dict_table:
            dict_table_config = {
                'table_name': table_name,
                'value_field': 'id',
                'display_field': 'name'
            }

        return {
            "status": "success",
            "fields": fields,
            "is_dict_table": is_dict_table,
            "dict_table_config": dict_table_config
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))