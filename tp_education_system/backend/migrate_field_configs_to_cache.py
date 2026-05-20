"""
迁移脚本：从字段配置文件导入数据到缓存表
"""
import json
import os
import psycopg2
from typing import Dict, List, Optional

DATABASE_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "database": "taiping_education",
    "user": "taiping_user",
    "password": "taiping_password"
}

FIELD_CONFIGS_DIR = os.path.join(os.path.dirname(__file__), 'config', 'field_configs')

def get_db_connection():
    return psycopg2.connect(**DATABASE_CONFIG)

def load_field_config(table_name: str) -> Optional[Dict]:
    config_files = [
        f"{table_name}.json",
        f"{table_name}字段配置.json",
        f"{table_name}字段配置.json"
    ]
    
    for filename in os.listdir(FIELD_CONFIGS_DIR):
        if filename.endswith('.json'):
            filepath = os.path.join(FIELD_CONFIGS_DIR, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    if config.get('table_name') == table_name or config.get('config_name') == table_name:
                        return config
            except Exception as e:
                print(f"[警告] 读取配置文件失败 {filename}: {e}")
    
    return None

def get_table_chinese_name(table_name: str) -> str:
    table_name_mappings_file = os.path.join(os.path.dirname(__file__), 'config', 'table_name_mappings.json')
    if os.path.exists(table_name_mappings_file):
        try:
            with open(table_name_mappings_file, 'r', encoding='utf-8') as f:
                mappings = json.load(f)
                return mappings.get('reverse_mappings', {}).get(table_name, table_name)
        except:
            pass
    return table_name

def get_field_chinese_name(field_name: str) -> str:
    field_name_mappings_file = os.path.join(os.path.dirname(__file__), 'config', 'field_name_mappings.json')
    if os.path.exists(field_name_mappings_file):
        try:
            with open(field_name_mappings_file, 'r', encoding='utf-8') as f:
                mappings = json.load(f)
                return mappings.get('reverse_mappings', {}).get(field_name, field_name)
        except:
            pass
    return field_name

def fetch_dict_values(dict_table: str, display_field: str) -> List[Dict]:
    if not dict_table or not display_field:
        return []
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = f'SELECT DISTINCT "{display_field}" FROM "{dict_table}" WHERE "{display_field}" IS NOT NULL ORDER BY "{display_field}"'
        cursor.execute(query)
        
        values = []
        for row in cursor.fetchall():
            value = row[0]
            if value:
                values.append({
                    "值": value,
                    "标签": value
                })
        
        cursor.close()
        conn.close()
        
        return values
    except Exception as e:
        print(f"[警告] 获取字典值失败 {dict_table}.{display_field}: {e}")
        return []

def migrate_field_configs():
    print("=" * 60)
    print("开始迁移字段配置到缓存表")
    print("=" * 60)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM table_field_relations")
    conn.commit()
    print("[OK] 已清空缓存表")
    
    migrated_tables = set()
    total_fields = 0
    total_dict_fields = 0
    
    for filename in os.listdir(FIELD_CONFIGS_DIR):
        if not filename.endswith('.json'):
            continue
        
        filepath = os.path.join(FIELD_CONFIGS_DIR, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            table_name = config.get('table_name')
            if not table_name:
                continue
            
            if table_name in migrated_tables:
                continue
            
            migrated_tables.add(table_name)
            
            table_name_cn = config.get('display_name') or config.get('chinese_title') or get_table_chinese_name(table_name)
            
            field_configs = config.get('field_configs', [])
            
            print(f"\n[处理] 表: {table_name_cn} ({table_name})")
            print(f"  字段数量: {len(field_configs)}")
            
            for field in field_configs:
                field_name = field.get('targetField')
                if not field_name:
                    continue
                
                field_name_cn = field.get('sourceField') or get_field_chinese_name(field_name)
                data_type = field.get('dataType', 'VARCHAR')
                relation_type = field.get('relation_type', 'none')
                relation_table = field.get('relation_table', '')
                relation_field = field.get('relation_display_field', '')
                
                dict_values = []
                dict_count = 0
                
                if relation_type == 'to_dict' and relation_table and relation_field:
                    dict_values = fetch_dict_values(relation_table, relation_field)
                    dict_count = len(dict_values)
                    total_dict_fields += 1
                    print(f"  ✓ 字段 {field_name_cn} ({field_name}): 关联字典 {relation_table}, 字典值数量: {dict_count}")
                else:
                    print(f"  - 字段 {field_name_cn} ({field_name}): {relation_type}")
                
                cursor.execute("""
                    INSERT INTO table_field_relations 
                    (table_name, 表名, field_name, 字段名, 数据类型, 关联类型, 关联表, 关联字段, 关联显示字段, 字典值列表, 字典值数量)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (table_name, field_name) 
                    DO UPDATE SET
                        表名 = EXCLUDED.表名,
                        字段名 = EXCLUDED.字段名,
                        数据类型 = EXCLUDED.数据类型,
                        关联类型 = EXCLUDED.关联类型,
                        关联表 = EXCLUDED.关联表,
                        关联字段 = EXCLUDED.关联字段,
                        关联显示字段 = EXCLUDED.关联显示字段,
                        字典值列表 = EXCLUDED.字典值列表,
                        字典值数量 = EXCLUDED.字典值数量,
                        更新时间 = CURRENT_TIMESTAMP
                """, (
                    table_name,
                    table_name_cn,
                    field_name,
                    field_name_cn,
                    data_type,
                    relation_type,
                    relation_table,
                    relation_field,
                    relation_field,
                    json.dumps(dict_values, ensure_ascii=False) if dict_values else None,
                    dict_count
                ))
                
                total_fields += 1
            
            conn.commit()
            
        except Exception as e:
            print(f"[错误] 处理配置文件失败 {filename}: {e}")
            continue
    
    cursor.close()
    conn.close()
    
    print("\n" + "=" * 60)
    print("迁移完成！")
    print("=" * 60)
    print(f"总计处理表数: {len(migrated_tables)}")
    print(f"总计处理字段数: {total_fields}")
    print(f"总计字典字段数: {total_dict_fields}")
    print("=" * 60)

if __name__ == "__main__":
    migrate_field_configs()
