#!/usr/bin/env python3
import json
import os

SCHEMA_FILE = r'd:\erp_thirteen\tp_education_system\backend\config\merged_schema_mappings.json'

if os.path.exists(SCHEMA_FILE):
    with open(SCHEMA_FILE, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    tables = config.get("tables", {})
    print(f"配置文件中共有 {len(tables)} 个表")
    
    if "retirement_report_data" in tables:
        print("\n找到 retirement_report_data 表配置:")
        table = tables["retirement_report_data"]
        print(f"  中文名: {table.get('chinese_name')}")
        print(f"  字段数: {len(table.get('fields', []))}")
        for field in table.get('fields', [])[:10]:
            print(f"    - {field.get('targetField') or field.get('english_name')}: {field.get('sourceField') or field.get('chinese_name')}")
    else:
        print("\n未找到 retirement_report_data 表配置")
        print("\n现有的表名:")
        for name in list(tables.keys())[:20]:
            print(f"  - {name}")
else:
    print(f"配置文件不存在: {SCHEMA_FILE}")
