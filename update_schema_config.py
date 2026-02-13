#!/usr/bin/env python3
"""
更新配置文件中的 retirement_report_data 表结构，使其与数据库一致
"""
import json
import os
import psycopg2

DATABASE_CONFIG = {
    'host': 'localhost',
    'port': '5432',
    'database': 'taiping_education',
    'user': 'taiping_user',
    'password': 'taiping_password'
}

SCHEMA_FILE = r'd:\erp_thirteen\tp_education_system\backend\config\merged_schema_mappings.json'

def get_table_fields_from_db(table_name):
    """从数据库获取表字段"""
    conn = psycopg2.connect(**DATABASE_CONFIG)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT column_name, data_type, is_nullable, character_maximum_length
        FROM information_schema.columns
        WHERE table_name = %s
        ORDER BY ordinal_position
    """, (table_name,))
    
    fields = []
    for row in cursor.fetchall():
        col_name, data_type, is_nullable, max_length = row
        
        # 映射PostgreSQL类型到通用类型
        type_mapping = {
            'character varying': 'VARCHAR',
            'text': 'TEXT',
            'integer': 'INTEGER',
            'bigint': 'INTEGER',
            'boolean': 'BOOLEAN',
            'date': 'DATE',
            'timestamp without time zone': 'DATETIME',
            'timestamp with time zone': 'DATETIME',
            'numeric': 'DECIMAL',
            'double precision': 'DECIMAL'
        }
        
        generic_type = type_mapping.get(data_type, 'VARCHAR')
        
        fields.append({
            'targetField': col_name,
            'english_name': col_name,
            'sourceField': col_name,  # 使用字段名本身作为中文名（因为已经是中文）
            'chinese_name': col_name,
            'dataType': generic_type,
            'data_type': generic_type,
            'required': is_nullable == 'NO',
            'length': max_length or 255
        })
    
    cursor.close()
    conn.close()
    return fields

def update_schema_config():
    # 读取配置文件
    with open(SCHEMA_FILE, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # 从数据库获取最新的字段列表
    fields = get_table_fields_from_db('retirement_report_data')
    
    print(f"从数据库获取到 {len(fields)} 个字段")
    
    # 更新表配置
    config['tables']['retirement_report_data'] = {
        'chinese_name': '退休呈报数据',
        'english_name': 'retirement_report_data',
        'table_type': 'master',
        'fields': fields
    }
    
    # 保存配置文件
    with open(SCHEMA_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    
    print("配置文件已更新！")
    print(f"\nretirement_report_data 表现在有 {len(fields)} 个字段")
    print("\n前20个字段:")
    for field in fields[:20]:
        print(f"  - {field['targetField']} ({field['dataType']})")

if __name__ == '__main__':
    update_schema_config()
