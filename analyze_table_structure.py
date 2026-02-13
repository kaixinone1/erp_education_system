#!/usr/bin/env python3
"""
分析表结构对比问题
"""

import psycopg2
import json

DB_PARAMS = {
    'host': 'localhost',
    'database': 'taiping_education',
    'user': 'taiping_user',
    'password': 'taiping_password'
}

def normalize_data_type(data_type):
    """标准化数据类型名称"""
    type_mapping = {
        'VARCHAR': 'STRING',
        'CHAR': 'STRING',
        'TEXT': 'STRING',
        'INTEGER': 'INTEGER',
        'INT': 'INTEGER',
        'BIGINT': 'INTEGER',
        'DECIMAL': 'DECIMAL',
        'NUMERIC': 'DECIMAL',
        'FLOAT': 'DECIMAL',
        'DOUBLE': 'DECIMAL',
        'DATE': 'DATE',
        'DATETIME': 'DATETIME',
        'TIMESTAMP': 'DATETIME',
        'BOOLEAN': 'BOOLEAN',
        'BOOL': 'BOOLEAN'
    }
    upper_type = str(data_type).upper()
    return type_mapping.get(upper_type, upper_type)

def get_table_signature_from_db(table_name):
    """从数据库获取表的字段签名"""
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = %s AND table_schema = 'public'
            ORDER BY column_name
        """, (table_name,))
        
        signature = []
        for row in cursor.fetchall():
            col_name = row[0]
            data_type = row[1]
            # 跳过系统字段
            if col_name in ['id', 'created_at', 'updated_at', 'import_batch', 'code', 'teacher_id']:
                continue
            normalized_type = normalize_data_type(data_type)
            signature.append((col_name.lower(), normalized_type))
        
        cursor.close()
        conn.close()
        
        return sorted(signature)
    except Exception as e:
        print(f"获取表 {table_name} 签名失败: {e}")
        return None

def main():
    # 读取配置文件中的签名
    config_file = r'd:\erp_thirteen\tp_education_system\backend\config\table_name_mappings.json'
    with open(config_file, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    print("=" * 70)
    print("表结构对比分析")
    print("=" * 70)
    
    for chinese_name, mapping in config.get('mappings', {}).items():
        english_name = mapping.get('english_name')
        saved_signature = mapping.get('field_signature', [])
        
        print(f"\n中文表名: {chinese_name}")
        print(f"英文表名: {english_name}")
        print("-" * 70)
        
        # 获取数据库中的实际签名
        db_signature = get_table_signature_from_db(english_name)
        
        print(f"\n配置文件中保存的签名 ({len(saved_signature)} 个字段):")
        for field in saved_signature:
            print(f"  {field}")
        
        print(f"\n数据库中实际的签名 ({len(db_signature)} 个字段):")
        if db_signature:
            for field in db_signature:
                print(f"  {field}")
        
        # 对比签名
        if saved_signature and db_signature:
            if saved_signature == db_signature:
                print("\n✓ 签名一致")
            else:
                print("\n✗ 签名不一致!")
                
                # 找出差异
                saved_set = set(tuple(x) for x in saved_signature)
                db_set = set(db_signature)
                
                only_in_saved = saved_set - db_set
                only_in_db = db_set - saved_set
                
                if only_in_saved:
                    print(f"  只在配置文件中存在: {only_in_saved}")
                if only_in_db:
                    print(f"  只在数据库中存在: {only_in_db}")
        
        print("=" * 70)

if __name__ == "__main__":
    main()
