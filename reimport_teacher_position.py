#!/usr/bin/env python3
"""
重新导入教师职务记录表 - 使用新的关联逻辑
"""

import sys
sys.path.append(r'd:\erp_thirteen\tp_education_system\backend')

from services.universal_import_service_v2 import UniversalImportServiceV2
import pandas as pd

def reimport_teacher_position():
    """重新导入教师职务记录表"""
    
    print("=" * 80)
    print("重新导入教师职务记录表")
    print("=" * 80)
    
    service = UniversalImportServiceV2()
    
    # 1. 首先确保字典表存在且有数据
    print("\n1. 检查/创建职务字典表...")
    
    # 从数据库读取现有字典数据，或创建新的
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
        # 检查旧字典表是否存在
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'dict_teacher_position_dictionary'
            )
        """)
        dict_exists = cursor.fetchone()[0]
        
        if dict_exists:
            # 读取现有字典数据（使用code和职务字段）
            cursor.execute("SELECT code, 职务 FROM dict_teacher_position_dictionary")
            dict_data = [{'code': row[0], 'name': row[1]} for row in cursor.fetchall()]
            print(f"  从旧字典表读取数据: {len(dict_data)} 条")
        else:
            # 创建默认字典数据
            dict_data = [
                {'code': '1', 'name': '正高级'},
                {'code': '2', 'name': '高级'},
                {'code': '3', 'name': '中级'},
                {'code': '4', 'name': '助理级'},
                {'code': '5', 'name': '员级'},
            ]
            print(f"  使用默认字典数据: {len(dict_data)} 条")
        
        # 2. 导入/更新字典表（使用新的表名 dict_position）
        print("\n2. 导入字典表到 dict_position...")
        result = service.import_dictionary(
            table_name='dict_position',
            data=dict_data,
            code_field='code',
            name_field='name'
        )
        print(f"  结果: {result}")
        
        # 3. 读取现有的教师职务记录数据
        print("\n3. 读取现有教师职务记录数据...")
        cursor.execute("""
            SELECT 姓名, 身份证号码, 职级, 任职文号, 起始日期, 认定日期
            FROM teacher_log
        """)
        rows = cursor.fetchall()
        
        if not rows:
            print("  没有数据需要重新导入")
            return
        
        print(f"  读取到 {len(rows)} 条记录")
        
        # 转换为字典列表
        child_data = []
        for row in rows:
            child_data.append({
                '姓名': row[0],
                '身份证号码': row[1],
                '职级': row[2],
                '任职文号': row[3],
                '起始日期': row[4],
                '认定日期': row[5]
            })
        
        # 4. 删除旧表
        print("\n4. 删除旧表 teacher_log...")
        cursor.execute("DROP TABLE IF EXISTS teacher_log")
        conn.commit()
        print("  旧表已删除")
        
    finally:
        cursor.close()
        conn.close()
    
    # 5. 使用新逻辑导入数据
    print("\n5. 使用新逻辑重新导入数据...")
    
    field_configs = [
        {'source_field': '姓名', 'target_field': 'name', 'data_type': 'VARCHAR', 'length': 50},
        {'source_field': '身份证号码', 'target_field': 'id_card', 'data_type': 'VARCHAR', 'length': 18},
        {'source_field': '职级', 'target_field': 'position_level', 'data_type': 'VARCHAR', 'length': 20,
         'link_to_dictionary': True, 'dictionary_table': 'dict_position'},
        {'source_field': '任职文号', 'target_field': 'appointment_no', 'data_type': 'VARCHAR', 'length': 50},
        {'source_field': '起始日期', 'target_field': 'start_date', 'data_type': 'DATE'},
        {'source_field': '认定日期', 'target_field': 'confirm_date', 'data_type': 'DATE'},
    ]
    
    result = service.import_child_table(
        table_name='teacher_log',
        field_configs=field_configs,
        data=child_data,
        table_type='child'
    )
    
    print(f"  导入结果: {result}")
    
    # 6. 验证数据
    print("\n6. 验证导入结果...")
    verify_reimport()
    
    print("\n" + "=" * 80)
    print("重新导入完成！")
    print("=" * 80)

def verify_reimport():
    """验证重新导入的数据"""
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
        # 查看新表结构
        print("\n  新表结构:")
        cursor.execute("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = 'teacher_log'
            ORDER BY ordinal_position
        """)
        for row in cursor.fetchall():
            print(f"    {row[0]}: {row[1]}")
        
        # 查看数据
        print("\n  导入的数据:")
        cursor.execute("""
            SELECT 
                name,
                id_card,
                position_level_id,
                position_level_名称,
                position_level_code,
                appointment_no
            FROM teacher_log
            LIMIT 10
        """)
        rows = cursor.fetchall()
        for row in rows:
            print(f"    姓名={row[0]}, 职级_id={row[2]}, 职级名称={row[3]}, 职级code={row[4]}")
        
        print(f"\n  共导入 {len(rows)} 条记录")
        
    except Exception as e:
        print(f"  验证失败: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    try:
        reimport_teacher_position()
    except Exception as e:
        print(f"重新导入失败: {e}")
        import traceback
        traceback.print_exc()
