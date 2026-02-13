#!/usr/bin/env python3
"""
测试个人身份导入功能
"""

import sys
sys.path.append(r'd:\erp_thirteen\tp_education_system\backend')

from services.universal_import_service_v2 import UniversalImportServiceV2

def test_import():
    """测试导入"""
    
    print("=" * 80)
    print("测试个人身份导入")
    print("=" * 80)
    
    service = UniversalImportServiceV2()
    
    # 模拟数据
    test_data = [
        {'姓名': '张三', '身份证号码': '110101200101011234', '个人身份': '1'},
        {'姓名': '李四', '身份证号码': '110101200101021235', '个人身份': '2'},
        {'姓名': '王五', '身份证号码': '110101200101031236', '个人身份': '1'},
    ]
    
    field_configs = [
        {'source_field': '姓名', 'target_field': 'name', 'data_type': 'VARCHAR', 'length': 50},
        {'source_field': '身份证号码', 'target_field': 'id_card', 'data_type': 'VARCHAR', 'length': 18},
        {'source_field': '个人身份', 'target_field': 'personal_identity', 'data_type': 'VARCHAR', 'length': 20,
         'link_to_dictionary': True, 'dictionary_table': 'dict_data_personal_identity',
         'dictionary_key_field': 'code', 'dictionary_display_field': 'name',
         'value_mapping': {'1': '干部', '2': '工人'}}
    ]
    
    result = service.import_child_table(
        table_name='test_personal_identity',
        field_configs=field_configs,
        data=test_data,
        table_type='child'
    )
    
    print(f"\n导入结果: {result}")
    
    # 验证数据
    if result['success']:
        verify_data()

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
            SELECT name, id_card, personal_identity_id, personal_identity_name, personal_identity_code
            FROM test_personal_identity
        """)
        
        for row in cursor.fetchall():
            print(f"  姓名={row[0]}, 身份_id={row[2]}, 身份_name={row[3]}, 身份_code={row[4]}")
        
        # 清理测试表
        cursor.execute("DROP TABLE IF EXISTS test_personal_identity")
        conn.commit()
        print("\n测试表已清理")
        
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    test_import()
