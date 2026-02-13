#!/usr/bin/env python3
"""
测试导入服务 V3
"""

import sys
sys.path.append(r'd:\erp_thirteen\tp_education_system\backend')

from services.universal_import_service_v3 import UniversalImportServiceV3

def test_import():
    """测试导入功能"""
    
    print("=" * 80)
    print("测试导入服务 V3 - 自动字典表管理")
    print("=" * 80)
    
    service = UniversalImportServiceV3()
    
    # 模拟数据 - 包含"人才类型"字段（之前没有字典表）
    test_data = [
        {'姓名': '张三', '身份证号码': '110101200101011234', '人才类型': '1', '个人身份': '1'},
        {'姓名': '李四', '身份证号码': '110101200101021235', '人才类型': '2', '个人身份': '2'},
        {'姓名': '王五', '身份证号码': '110101200101031236', '人才类型': '1', '个人身份': '1'},
    ]
    
    field_configs = [
        {'source_field': '姓名', 'target_field': 'name', 'data_type': 'VARCHAR', 'length': 50},
        {'source_field': '身份证号码', 'target_field': 'id_card', 'data_type': 'VARCHAR', 'length': 18},
        {'source_field': '人才类型', 'target_field': 'talent_type', 'data_type': 'VARCHAR', 'length': 20,
         'link_to_dictionary': True, 'dictionary_table': 'dict_talent_type',
         'value_mapping': {'1': '高层次人才', '2': '普通人才'}},
        {'source_field': '个人身份', 'target_field': 'personal_identity', 'data_type': 'VARCHAR', 'length': 20,
         'link_to_dictionary': True, 'dictionary_table': 'dict_data_personal_identity',
         'value_mapping': {'1': '干部', '2': '工人'}},
    ]
    
    result = service.import_data(
        table_name='test_import_v3',
        field_configs=field_configs,
        data=test_data,
        auto_manage_dict=True
    )
    
    print(f"\n导入结果:")
    print(f"  成功: {result['success']}")
    print(f"  插入条数: {result['inserted']}")
    print(f"  创建的字典表: {result['dict_tables_created']}")
    
    if result['success']:
        verify_data(service)
    
    service.close()

def verify_data(service):
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
                   talent_type_id, talent_type_name, talent_type_code,
                   personal_identity_id, personal_identity_name, personal_identity_code
            FROM test_import_v3
        """)
        
        for row in cursor.fetchall():
            print(f"\n  姓名: {row[0]}")
            print(f"    人才类型: id={row[2]}, name={row[3]}, code={row[4]}")
            print(f"    个人身份: id={row[5]}, name={row[6]}, code={row[7]}")
        
        # 清理测试表
        cursor.execute("DROP TABLE IF EXISTS test_import_v3")
        conn.commit()
        print("\n测试表已清理")
        
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    test_import()
