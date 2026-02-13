#!/usr/bin/env python3
"""
检查验证环节，看看数据是否被标记为无效
"""

import pandas as pd
import os
import sys

sys.path.append(r'd:\erp_thirteen\tp_education_system\backend')
from services.validation_service import ValidationService

def check():
    # 1. 读取上传的文件
    upload_dir = r'd:\erp_thirteen\tp_education_system\backend\uploads'
    files = [f for f in os.listdir(upload_dir) if f.endswith(('.xlsx', '.xls', '.csv'))]
    files.sort(reverse=True)
    latest_file = files[0]
    file_path = os.path.join(upload_dir, latest_file)
    
    print(f"检查文件: {latest_file}")
    print("=" * 80)
    
    # 2. 读取文件
    if latest_file.endswith('.csv'):
        df = pd.read_csv(file_path)
    else:
        df = pd.read_excel(file_path)
    
    # 3. 准备数据
    data = df.to_dict(orient='records')
    for row in data:
        for key, value in row.items():
            if pd.isna(value):
                row[key] = None
    
    print(f"总数据条数: {len(data)}")
    print()
    
    # 4. 准备字段配置
    field_configs = [
        {"sourceField": "姓名", "targetField": "姓名", "dataType": "VARCHAR", "length": 255},
        {"sourceField": "身份证号码", "targetField": "身份证号码", "dataType": "VARCHAR", "length": 255},
        {"sourceField": "学历类型", "targetField": "学历类型", "dataType": "VARCHAR", "length": 255},
        {"sourceField": "学历", "targetField": "学历", "dataType": "VARCHAR", "length": 255},
        {"sourceField": "学位", "targetField": "学位", "dataType": "VARCHAR", "length": 255},
        {"sourceField": "毕业院校", "targetField": "毕业院校", "dataType": "VARCHAR", "length": 255},
        {"sourceField": "专业", "targetField": "专业", "dataType": "VARCHAR", "length": 255},
        {"sourceField": "毕业日期", "targetField": "毕业日期", "dataType": "DATE"}
    ]
    
    # 5. 获取父表数据用于 Level 4 验证
    import psycopg2
    DB_PARAMS = {
        'host': 'localhost',
        'database': 'taiping_education',
        'user': 'taiping_user',
        'password': 'taiping_password'
    }
    conn = psycopg2.connect(**DB_PARAMS)
    cursor = conn.cursor()
    cursor.execute('SELECT 身份证号码 FROM teacher_basic WHERE 身份证号码 IS NOT NULL')
    parent_id_cards = set(row[0] for row in cursor.fetchall())
    cursor.close()
    conn.close()
    
    parent_data = {'id_cards': parent_id_cards}
    
    # 6. 进行 Level 4 验证
    print("进行 Level 4 验证（外键完整性验证）...")
    service = ValidationService()
    result = service.validate_data(
        data=data,
        field_configs=field_configs,
        validation_level=4,
        table_type="child",
        parent_data=parent_data
    )
    
    print()
    print("=" * 80)
    print("验证结果:")
    print("=" * 80)
    print(f"总数据: {result['summary']['total_rows']} 条")
    print(f"有效数据: {result['summary']['valid_rows']} 条")
    print(f"无效数据: {result['summary']['invalid_rows']} 条")
    print(f"总错误数: {result['summary']['total_errors']} 条")
    print()
    
    # 7. 显示前10条无效数据
    invalid_rows = [r for r in result['validated_data'] if not r['is_valid']]
    if invalid_rows:
        print(f"前10条无效数据:")
        for row in invalid_rows[:10]:
            print(f"  第{row['row_index'] + 1}行:")
            print(f"    数据: {row['data']}")
            print(f"    错误: {row['errors']}")
    
    return result

if __name__ == "__main__":
    check()
