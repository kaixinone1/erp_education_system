#!/usr/bin/env python3
"""
测试V3导入服务 - 通用字典表结构
"""

import sys
sys.path.append(r'd:\erp_thirteen\tp_education_system\backend')

from services.universal_import_service_v3 import UniversalImportServiceV3

def test_dict_import():
    """测试字典表导入"""
    print("=" * 80)
    print("测试字典表导入")
    print("=" * 80)
    
    service = UniversalImportServiceV3()
    
    # 模拟字典表数据（只有一个字段"人才类型"）
    dict_data = [
        {'人才类型': '专业技术人才'},
        {'人才类型': '技术人才'},
        {'人才类型': '管理人员'},
        {'人才类型': '退休人员'},
    ]
    
    field_configs = [
        {'source_field': '人才类型', 'target_field': 'name', 'data_type': 'VARCHAR', 'length': 50}
    ]
    
    result = service.import_data(
        table_name='dict_test_talent',
        field_configs=field_configs,
        data=dict_data,
        auto_manage_dict=False  # 不自动管理字典表
    )
    
    print(f"\n字典表导入结果:")
    print(f"  成功: {result['success']}")
    print(f"  插入条数: {result['inserted']}")
    
    service.close()
    return result['success']

def test_child_import():
    """测试子表导入（关联字典表）"""
    print("\n" + "=" * 80)
    print("测试子表导入（关联字典表）")
    print("=" * 80)
    
    service = UniversalImportServiceV3()
    
    # 模拟子表数据（人才类型字段值是字典表的id：1, 2, 3, 4）
    child_data = [
        {'姓名': '张三', '身份证号码': '110101200101011234', '人才类型': 1},
        {'姓名': '李四', '身份证号码': '110101200101021235', '人才类型': 2},
        {'姓名': '王五', '身份证号码': '110101200101031236', '人才类型': 1},
    ]
    
    field_configs = [
        {'source_field': '姓名', 'target_field': 'name', 'data_type': 'VARCHAR', 'length': 50},
        {'source_field': '身份证号码', 'target_field': 'id_card', 'data_type': 'VARCHAR', 'length': 18},
        {'source_field': '人才类型', 'target_field': 'talent_type', 'data_type': 'INTEGER',
         'link_to_dictionary': True, 'dictionary_table': 'dict_test_talent'}
    ]
    
    result = service.import_data(
        table_name='teacher_test_talent',
        field_configs=field_configs,
        data=child_data,
        auto_manage_dict=False
    )
    
    print(f"\n子表导入结果:")
    print(f"  成功: {result['success']}")
    print(f"  插入条数: {result['inserted']}")
    
    if result['success']:
        verify_data(service)
    
    service.close()
    return result['success']

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
            SELECT name, id_card, talent_type_id, talent_type_name
            FROM teacher_test_talent
        """)
        
        for row in cursor.fetchall():
            print(f"\n  姓名: {row[0]}")
            print(f"    人才类型: id={row[2]}, name={row[3]}")
        
        # 清理测试表
        cursor.execute("DROP TABLE IF EXISTS teacher_test_talent")
        cursor.execute("DROP TABLE IF EXISTS dict_test_talent")
        conn.commit()
        print("\n测试表已清理")
        
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    # 先测试字典表导入
    if test_dict_import():
        # 再测试子表导入
        test_child_import()
