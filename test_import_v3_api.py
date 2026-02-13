#!/usr/bin/env python3
"""
测试V3导入API
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_import():
    """测试导入API"""
    
    print("=" * 80)
    print("测试V3导入API")
    print("=" * 80)
    
    # 测试数据
    test_data = [
        {'姓名': '张三', '身份证号码': '110101200101011234', '人才类型': '1'},
        {'姓名': '李四', '身份证号码': '110101200101021235', '人才类型': '2'},
    ]
    
    field_configs = [
        {'source_field': '姓名', 'target_field': 'name', 'data_type': 'VARCHAR', 'length': 50},
        {'source_field': '身份证号码', 'target_field': 'id_card', 'data_type': 'VARCHAR', 'length': 18},
        {'source_field': '人才类型', 'target_field': 'talent_type', 'data_type': 'VARCHAR', 'length': 20,
         'link_to_dictionary': True, 'dictionary_table': 'dict_talent_type',
         'value_mapping': {'1': '高层次人才', '2': '普通人才'}}
    ]
    
    payload = {
        'table_name': 'test_teacher_talent',
        'field_configs': field_configs,
        'data': test_data,
        'chinese_title': '测试教师人才类型',
        'table_type': 'child'
    }
    
    print(f"\n发送请求...")
    print(f"URL: {BASE_URL}/api/import/import-v3")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/import/import-v3",
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"状态码: {response.status_code}")
        result = response.json()
        print(f"\n返回结果:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
        if response.ok and result.get('success'):
            verify_data()
        
    except Exception as e:
        print(f"请求失败: {e}")
        import traceback
        traceback.print_exc()

def verify_data():
    """验证数据"""
    import psycopg2
    
    DB_PARAMS = {
        'host': 'localhost',
        'database': 'taiping_education',
        'user': 'taiping_user',
        'password': 'taiping_password'
    }
    
    conn = psycopg2.connect(**DB_PARAMS)
    cursor = conn.cursor()
    
    try:
        print("\n验证导入的数据:")
        cursor.execute("""
            SELECT name, id_card, 
                   talent_type_id, talent_type_name, talent_type_code
            FROM test_teacher_talent
        """)
        
        for row in cursor.fetchall():
            print(f"\n  姓名: {row[0]}")
            print(f"    人才类型: id={row[2]}, name={row[3]}, code={row[4]}")
        
        # 清理测试表
        cursor.execute("DROP TABLE IF EXISTS test_teacher_talent")
        conn.commit()
        print("\n测试表已清理")
        
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    test_import()
