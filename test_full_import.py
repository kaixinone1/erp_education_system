#!/usr/bin/env python3
"""
测试完整导入流程
"""

import pandas as pd
import os
import sys

sys.path.append(r'd:\erp_thirteen\tp_education_system\backend')
from services.import_service import ImportService

def test_import():
    # 1. 读取上传的文件
    upload_dir = r'd:\erp_thirteen\tp_education_system\backend\uploads'
    files = [f for f in os.listdir(upload_dir) if f.endswith(('.xlsx', '.xls', '.csv'))]
    files.sort(reverse=True)
    latest_file = files[0]
    file_path = os.path.join(upload_dir, latest_file)
    
    print(f"测试导入文件: {latest_file}")
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
    
    print(f"准备导入的数据条数: {len(data)}")
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
    
    # 5. 执行导入
    service = ImportService()
    
    try:
        result = service.import_data(
            table_name='teacher_record',
            field_configs=field_configs,
            data=data,
            module_id='module-test',
            module_name='测试模块',
            table_type='child',
            parent_table='teacher_basic',
            file_name=latest_file,
            chinese_title='教师学历记录',
            sub_module_id='',
            sub_module_name=''
        )
        
        print()
        print("=" * 80)
        print("导入结果:")
        print("=" * 80)
        print(f"状态: {result.get('status')}")
        print(f"消息: {result.get('message')}")
        print(f"记录数: {result.get('record_count')}")
        print(f"是否已存在表: {result.get('is_existing_table')}")
        
        if 'errors' in result:
            print(f"\n错误数: {len(result['errors'])}")
            for error in result['errors'][:10]:
                print(f"  - {error}")
        
    except Exception as e:
        print(f"导入失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_import()
