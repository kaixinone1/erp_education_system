#!/usr/bin/env python3
"""
测试通用导入服务 V2 - 验证自动关联功能
"""

import sys
sys.path.append(r'd:\erp_thirteen\tp_education_system\backend')

from services.universal_import_service_v2 import UniversalImportServiceV2
import pandas as pd
import io

def test_import_dictionary():
    """测试字典表导入"""
    print("=" * 80)
    print("测试1: 字典表导入")
    print("=" * 80)
    
    service = UniversalImportServiceV2()
    
    # 模拟字典数据
    dict_data = [
        {'序号': '1', '职务': '正高级'},
        {'序号': '2', '职务': '高级'},
        {'序号': '3', '职务': '中级'},
        {'序号': '4', '职务': '助理级'},
        {'序号': '5', '职务': '员级'},
    ]
    
    result = service.import_dictionary(
        table_name='dict_position',
        data=dict_data,
        code_field='序号',
        name_field='职务'
    )
    
    print(f"字典表导入结果: {result}")
    return result['success']

def test_import_child_table():
    """测试子表导入（自动关联）"""
    print("\n" + "=" * 80)
    print("测试2: 子表导入（自动关联主表和字典表）")
    print("=" * 80)
    
    service = UniversalImportServiceV2()
    
    # 字段配置
    field_configs = [
        {'source_field': '姓名', 'target_field': 'name', 'data_type': 'VARCHAR', 'length': 50},
        {'source_field': '身份证号码', 'target_field': 'id_card', 'data_type': 'VARCHAR', 'length': 18},
        {'source_field': '职级', 'target_field': 'position_level', 'data_type': 'VARCHAR', 'length': 20,
         'link_to_dictionary': True, 'dictionary_table': 'dict_position'},
        {'source_field': '任职文号', 'target_field': 'appointment_no', 'data_type': 'VARCHAR', 'length': 50},
    ]
    
    # 模拟子表数据
    child_data = [
        {'姓名': '张三', '身份证号码': '110101200101011234', '职级': '3', '任职文号': '2023-001'},
        {'姓名': '张三', '身份证号码': '110101200101011234', '职级': '2', '任职文号': '2024-001'},
        {'姓名': '李四', '身份证号码': '110101200101021235', '职级': '3', '任职文号': '2023-002'},
    ]
    
    result = service.import_child_table(
        table_name='teacher_position',
        field_configs=field_configs,
        data=child_data,
        table_type='child'
    )
    
    print(f"子表导入结果: {result}")
    return result['success']

def verify_data():
    """验证导入的数据"""
    print("\n" + "=" * 80)
    print("测试3: 验证导入的数据")
    print("=" * 80)
    
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
        # 查看字典表
        print("\n字典表数据 (dict_position):")
        cursor.execute("SELECT id, code, name FROM dict_position ORDER BY id")
        for row in cursor.fetchall():
            print(f"  id={row[0]}, code={row[1]}, name={row[2]}")
        
        # 查看子表数据
        print("\n子表数据 (teacher_position):")
        cursor.execute("""
            SELECT id, teacher_id, name, id_card, 
                   position_level_id, position_level_名称, position_level_code,
                   appointment_no
            FROM teacher_position
            ORDER BY id
        """)
        rows = cursor.fetchall()
        for row in rows:
            print(f"  id={row[0]}, teacher_id={row[1]}, name={row[2]}, "
                  f"职级_id={row[4]}, 职级名称={row[5]}, 职级code={row[6]}")
        
        # 验证关联查询
        print("\n关联查询验证:")
        cursor.execute("""
            SELECT 
                tp.name,
                tp.id_card,
                tp.position_level_名称,
                tp.appointment_no
            FROM teacher_position tp
            ORDER BY tp.id
        """)
        for row in cursor.fetchall():
            print(f"  姓名={row[0]}, 身份证={row[1]}, 职级={row[2]}, 文号={row[3]}")
        
        return True
        
    except Exception as e:
        print(f"验证失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        cursor.close()
        conn.close()

def cleanup():
    """清理测试数据"""
    print("\n" + "=" * 80)
    print("清理测试数据")
    print("=" * 80)
    
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
        cursor.execute("DROP TABLE IF EXISTS teacher_position")
        cursor.execute("DROP TABLE IF EXISTS dict_position")
        conn.commit()
        print("✅ 测试表已删除")
    except Exception as e:
        print(f"清理失败: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    try:
        # 先清理可能存在的旧表
        cleanup()
        
        # 测试字典表导入
        dict_success = test_import_dictionary()
        
        # 测试子表导入
        child_success = test_import_child_table()
        
        # 验证数据
        verify_success = verify_data()
        
        print("\n" + "=" * 80)
        print("测试总结")
        print("=" * 80)
        print(f"字典表导入: {'✅ 成功' if dict_success else '❌ 失败'}")
        print(f"子表导入: {'✅ 成功' if child_success else '❌ 失败'}")
        print(f"数据验证: {'✅ 通过' if verify_success else '❌ 失败'}")
        
        if dict_success and child_success and verify_success:
            print("\n🎉 所有测试通过！通用导入服务 V2 工作正常！")
        else:
            print("\n⚠️ 部分测试失败，请检查日志")
        
        # 最后清理
        cleanup()
        
    except Exception as e:
        print(f"\n测试异常: {e}")
        import traceback
        traceback.print_exc()
