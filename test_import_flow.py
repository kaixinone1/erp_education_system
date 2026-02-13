#!/usr/bin/env python3
"""
测试导入流程 - 字典表、子表、主表
"""

import sys
sys.path.append(r'd:\erp_thirteen\tp_education_system\backend')

from services.universal_import_service_v3 import UniversalImportServiceV3
import psycopg2

DB_PARAMS = {
    'host': 'localhost',
    'database': 'taiping_education',
    'user': 'taiping_user',
    'password': 'taiping_password'
}

def test_dict_import():
    """测试字典表导入"""
    print("\n" + "="*80)
    print("阶段1: 导入字典表 - 人才类型")
    print("="*80)
    
    service = UniversalImportServiceV3()
    
    # 字典表数据
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
        table_name='dict_talent_type',
        field_configs=field_configs,
        data=dict_data,
        auto_manage_dict=False
    )
    
    print(f"\n字典表导入结果:")
    print(f"  成功: {result['success']}")
    print(f"  插入条数: {result['inserted']}")
    
    service.close()
    return result['success']

def test_child_import():
    """测试子表导入（关联字典表）"""
    print("\n" + "="*80)
    print("阶段2: 导入子表 - 教师人才类型（关联字典表）")
    print("="*80)
    
    service = UniversalImportServiceV3()
    
    # 子表数据（人才类型字段值是字典表的id：1, 2, 3, 4）
    child_data = [
        {'姓名': '张三', '身份证号码': '110101200101011234', '人才类型': 1},
        {'姓名': '李四', '身份证号码': '110101200101021235', '人才类型': 2},
        {'姓名': '王五', '身份证号码': '110101200101031236', '人才类型': 1},
    ]
    
    field_configs = [
        {'source_field': '姓名', 'target_field': 'name', 'data_type': 'VARCHAR', 'length': 50},
        {'source_field': '身份证号码', 'target_field': 'id_card', 'data_type': 'VARCHAR', 'length': 18},
        {'source_field': '人才类型', 'target_field': 'talent_type', 'data_type': 'INTEGER',
         'link_to_dictionary': True, 'dictionary_table': 'dict_talent_type'}
    ]
    
    result = service.import_data(
        table_name='teacher_talent_type',
        field_configs=field_configs,
        data=child_data,
        auto_manage_dict=False
    )
    
    print(f"\n子表导入结果:")
    print(f"  成功: {result['success']}")
    print(f"  插入条数: {result['inserted']}")
    
    service.close()
    return result['success']

def test_master_import():
    """测试主表导入"""
    print("\n" + "="*80)
    print("阶段3: 导入主表 - 教师基本信息")
    print("="*80)
    
    service = UniversalImportServiceV3()
    
    # 主表数据
    master_data = [
        {
            '姓名': '张三',
            '身份证号码': '110101200101011234',
            '档案出生日期': '2001-01-01',
            '民族': '汉族',
            '籍贯': '北京市',
            '联系电话': '13800138001',
            '参加工作日期': '2020-07-01',
            '进入本单位日期': '2020-07-01',
            '任职状态': '在职'
        },
        {
            '姓名': '李四',
            '身份证号码': '110101200101021235',
            '档案出生日期': '2001-01-02',
            '民族': '汉族',
            '籍贯': '北京市',
            '联系电话': '13800138002',
            '参加工作日期': '2019-08-01',
            '进入本单位日期': '2019-08-01',
            '任职状态': '在职'
        },
        {
            '姓名': '王五',
            '身份证号码': '110101200101031236',
            '档案出生日期': '2001-01-03',
            '民族': '满族',
            '籍贯': '北京市',
            '联系电话': '13800138003',
            '参加工作日期': '2018-09-01',
            '进入本单位日期': '2018-09-01',
            '任职状态': '在职'
        }
    ]
    
    field_configs = [
        {'source_field': '姓名', 'target_field': '姓名', 'data_type': 'VARCHAR', 'length': 50},
        {'source_field': '身份证号码', 'target_field': '身份证号码', 'data_type': 'VARCHAR', 'length': 18},
        {'source_field': '档案出生日期', 'target_field': '档案出生日期', 'data_type': 'DATE'},
        {'source_field': '民族', 'target_field': '民族', 'data_type': 'VARCHAR', 'length': 20},
        {'source_field': '籍贯', 'target_field': '籍贯', 'data_type': 'VARCHAR', 'length': 50},
        {'source_field': '联系电话', 'target_field': '联系电话', 'data_type': 'VARCHAR', 'length': 20},
        {'source_field': '参加工作日期', 'target_field': '参加工作日期', 'data_type': 'DATE'},
        {'source_field': '进入本单位日期', 'target_field': '进入本单位日期', 'data_type': 'DATE'},
        {'source_field': '任职状态', 'target_field': '任职状态', 'data_type': 'VARCHAR', 'length': 20}
    ]
    
    result = service.import_data(
        table_name='teacher_basic',
        field_configs=field_configs,
        data=master_data,
        auto_manage_dict=False
    )
    
    print(f"\n主表导入结果:")
    print(f"  成功: {result['success']}")
    print(f"  插入条数: {result['inserted']}")
    
    service.close()
    return result['success']

def verify_data():
    """验证数据"""
    print("\n" + "="*80)
    print("验证导入的数据")
    print("="*80)
    
    conn = psycopg2.connect(**DB_PARAMS)
    cursor = conn.cursor()
    
    # 验证字典表
    print("\n1. 字典表数据:")
    cursor.execute("SELECT id, name FROM dict_talent_type ORDER BY id")
    for row in cursor.fetchall():
        print(f"  id={row[0]}, name={row[1]}")
    
    # 验证主表
    print("\n2. 主表数据:")
    cursor.execute("SELECT id, 姓名, 身份证号码 FROM teacher_basic ORDER BY id")
    for row in cursor.fetchall():
        print(f"  id={row[0]}, 姓名={row[1]}, 身份证={row[2]}")
    
    # 验证子表
    print("\n3. 子表数据（关联字典表）:")
    cursor.execute("""
        SELECT t.name, t.id_card, t.talent_type_id, t.talent_type_name
        FROM teacher_talent_type t
        ORDER BY t.id
    """)
    for row in cursor.fetchall():
        print(f"  姓名={row[0]}, 身份证={row[1]}, 人才类型id={row[2]}, 人才类型={row[3]}")
    
    cursor.close()
    conn.close()
    
    print("\n" + "="*80)
    print("验证完成！")
    print("="*80)

def cleanup_test_tables():
    """清理测试表"""
    print("\n" + "="*80)
    print("清理测试表")
    print("="*80)
    
    conn = psycopg2.connect(**DB_PARAMS)
    cursor = conn.cursor()
    
    tables = ['teacher_talent_type', 'dict_talent_type', 'teacher_basic']
    for table in tables:
        try:
            cursor.execute(f"DROP TABLE IF EXISTS {table} CASCADE")
            print(f"  ✓ 已删除: {table}")
        except Exception as e:
            print(f"  ✗ 删除失败 {table}: {e}")
    
    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    # 先清理测试表
    cleanup_test_tables()
    
    # 按顺序导入
    # 注意：主表需要在子表之前导入，因为子表要关联主表
    if test_master_import():
        if test_dict_import():
            if test_child_import():
                verify_data()
            else:
                print("\n✗ 子表导入失败")
        else:
            print("\n✗ 字典表导入失败")
    else:
        print("\n✗ 主表导入失败")
