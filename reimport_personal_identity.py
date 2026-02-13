#!/usr/bin/env python3
"""
重新导入个人身份表 - 使用新的关联字段
"""

import sys
sys.path.append(r'd:\erp_thirteen\tp_education_system\backend')

from services.universal_import_service_v2 import UniversalImportServiceV2
import psycopg2

DB_PARAMS = {
    'host': 'localhost',
    'database': 'taiping_education',
    'user': 'taiping_user',
    'password': 'taiping_password'
}

def reimport_personal_identity():
    """重新导入个人身份表"""
    
    print("=" * 80)
    print("重新导入个人身份表")
    print("=" * 80)
    
    service = UniversalImportServiceV2()
    
    conn = psycopg2.connect(**DB_PARAMS)
    cursor = conn.cursor()
    
    try:
        # 1. 读取现有数据
        print("\n1. 读取现有数据...")
        cursor.execute("""
            SELECT 姓名, 身份证号码, 个人身份
            FROM teacher_personal_identity
        """)
        rows = cursor.fetchall()
        print(f"  读取到 {len(rows)} 条记录")
        
        if not rows:
            print("  没有数据需要重新导入")
            return
        
        # 转换为字典列表
        data = []
        for row in rows:
            data.append({
                '姓名': row[0],
                '身份证号码': row[1],
                '个人身份': row[2]
            })
        
        # 2. 删除旧表
        print("\n2. 删除旧表...")
        cursor.execute("DROP TABLE IF EXISTS teacher_personal_identity")
        conn.commit()
        print("  旧表已删除")
        
    finally:
        cursor.close()
        conn.close()
    
    # 3. 使用新逻辑导入
    print("\n3. 使用新逻辑导入数据...")
    
    field_configs = [
        {'source_field': '姓名', 'target_field': 'name', 'data_type': 'VARCHAR', 'length': 50},
        {'source_field': '身份证号码', 'target_field': 'id_card', 'data_type': 'VARCHAR', 'length': 18},
        {'source_field': '个人身份', 'target_field': 'personal_identity', 'data_type': 'VARCHAR', 'length': 20,
         'link_to_dictionary': True, 'dictionary_table': 'dict_data_personal_identity',
         'dictionary_key_field': 'code', 'dictionary_display_field': 'name',
         'value_mapping': {'1': '干部', '2': '工人'}}
    ]
    
    result = service.import_child_table(
        table_name='teacher_personal_identity',
        field_configs=field_configs,
        data=data,
        table_type='child'
    )
    
    print(f"  导入结果: {result}")
    
    # 4. 验证数据
    if result['success']:
        verify_data()

def verify_data():
    """验证数据"""
    conn = psycopg2.connect(**DB_PARAMS)
    cursor = conn.cursor()
    
    try:
        print("\n4. 验证新表结构...")
        cursor.execute("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = 'teacher_personal_identity'
            ORDER BY ordinal_position
        """)
        print("  新表字段:")
        for row in cursor.fetchall():
            print(f"    {row[0]}: {row[1]}")
        
        print("\n5. 验证导入的数据...")
        cursor.execute("""
            SELECT name, id_card, personal_identity_id, personal_identity_name, personal_identity_code
            FROM teacher_personal_identity
            LIMIT 10
        """)
        
        rows = cursor.fetchall()
        print(f"  共 {len(rows)} 条记录:")
        for row in rows:
            print(f"    姓名={row[0]}, 身份_id={row[2]}, 身份_name={row[3]}, 身份_code={row[4]}")
        
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    try:
        reimport_personal_identity()
        print("\n" + "=" * 80)
        print("重新导入完成！请刷新页面查看结果。")
        print("=" * 80)
    except Exception as e:
        print(f"\n重新导入失败: {e}")
        import traceback
        traceback.print_exc()
