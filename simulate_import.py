#!/usr/bin/env python3
"""
模拟导入过程，检查数据在哪个环节被过滤
"""

import pandas as pd
import psycopg2
import os
import sys

sys.path.append(r'd:\erp_thirteen\tp_education_system\backend')
from services.import_service import ImportService

DB_PARAMS = {
    'host': 'localhost',
    'database': 'taiping_education',
    'user': 'taiping_user',
    'password': 'taiping_password'
}

def simulate():
    # 1. 读取上传的文件
    upload_dir = r'd:\erp_thirteen\tp_education_system\backend\uploads'
    files = [f for f in os.listdir(upload_dir) if f.endswith(('.xlsx', '.xls', '.csv'))]
    files.sort(reverse=True)
    latest_file = files[0]
    file_path = os.path.join(upload_dir, latest_file)
    
    print(f"模拟导入文件: {latest_file}")
    print("=" * 80)
    
    # 2. 读取文件
    if latest_file.endswith('.csv'):
        df = pd.read_csv(file_path)
    else:
        df = pd.read_excel(file_path)
    
    # 3. 准备字段配置（模拟前端配置）
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
    
    # 4. 准备数据
    data = df.to_dict(orient='records')
    
    # 转换NaN为None
    for row in data:
        for key, value in row.items():
            if pd.isna(value):
                row[key] = None
    
    print(f"准备导入的数据条数: {len(data)}")
    print()
    
    # 5. 获取父表ID映射
    service = ImportService()
    parent_id_map = service._get_parent_id_map('teacher_basic')
    
    print(f"父表ID映射数量: {len(parent_id_map)}")
    print()
    
    # 6. 检查每条数据的匹配情况
    matched_count = 0
    not_matched = []
    
    for idx, row in enumerate(data, 1):
        id_card = str(row.get('身份证号码', '')).strip()
        if id_card in parent_id_map:
            matched_count += 1
        else:
            not_matched.append((idx, id_card))
    
    print(f"能匹配父表的数据: {matched_count} 条")
    print(f"不能匹配父表的数据: {len(not_matched)} 条")
    
    if not_matched:
        print("\n不能匹配的前10条:")
        for idx, id_card in not_matched[:10]:
            print(f"  第{idx}行: {id_card}")
    
    print()
    print("=" * 80)
    print("结论:")
    print("=" * 80)
    print(f"文件总数据: {len(data)} 条")
    print(f"能匹配主表: {matched_count} 条")
    print(f"不能匹配主表: {len(not_matched)} 条")
    print()
    print("理论上应该能导入 {matched_count} 条数据")
    print("如果实际导入数量不对，需要检查导入逻辑")

if __name__ == "__main__":
    simulate()
