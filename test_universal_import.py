#!/usr/bin/env python3
"""
测试通用导入服务
"""

import sys
sys.path.append(r'd:\erp_thirteen\tp_education_system\backend')

from services.universal_import_service import UniversalImportService
import pandas as pd
import io

def test_analyze_file():
    """测试文件分析功能"""
    print("=" * 80)
    print("测试通用导入服务 - 文件分析")
    print("=" * 80)
    
    # 创建测试数据
    test_data = {
        '姓名': ['张三', '李四', '王五'],
        '性别': ['男', '女', '男'],
        '出生日期': ['2001/1/1', '2001/01/01', '2001-01-01'],
        '身份证号码': ['110101200101011234', '110101200101021235', '110101200101031236'],
        '手机号码': ['13800138000', '13900139000', '13700137000'],
        '学历': ['本科', '硕士', '博士'],
        '工资': ['5000.50', '8000.00', '12000.00'],
        '年龄': ['25', '26', '27'],
        '备注': ['测试数据1', '测试数据2', '测试数据3']
    }
    df = pd.DataFrame(test_data)
    
    # 保存到内存
    excel_buffer = io.BytesIO()
    df.to_excel(excel_buffer, index=False, engine='openpyxl')
    excel_buffer.seek(0)
    
    # 初始化服务
    service = UniversalImportService()
    
    # 分析文件
    result = service.analyze_file(excel_buffer.getvalue(), 'test_data.xlsx')
    
    print("\n分析结果:")
    print(f"字段列表: {result['fields']}")
    print(f"总行数: {result['total_rows']}")
    print("\n字段映射建议:")
    for mapping in result['suggested_mappings']:
        print(f"  {mapping['source_field']} -> {mapping['target_field']} ({mapping['data_type']}, 置信度: {mapping['confidence']})")
    
    print("\n预览数据（日期应已转换）:")
    for i, row in enumerate(result['preview_data']):
        print(f"  行{i+1}: {row}")
    
    return result

def test_validate_data():
    """测试数据验证功能"""
    print("\n" + "=" * 80)
    print("测试通用导入服务 - 数据验证")
    print("=" * 80)
    
    service = UniversalImportService()
    
    # 测试数据
    data = [
        {'姓名': '张三', '身份证号码': '110101200101011234', '手机号码': '13800138000'},
        {'姓名': '李四', '身份证号码': 'invalid_id', '手机号码': 'invalid_phone'},
    ]
    
    field_configs = [
        {'source_field': '姓名', 'target_field': 'name', 'data_type': 'VARCHAR'},
        {'source_field': '身份证号码', 'target_field': 'id_card', 'data_type': 'VARCHAR'},
        {'source_field': '手机号码', 'target_field': 'phone', 'data_type': 'VARCHAR'},
    ]
    
    result = service.validate_data(data, field_configs)
    
    print(f"\n验证结果:")
    print(f"是否有效: {result['valid']}")
    print(f"错误数: {len(result['errors'])}")
    if result['errors']:
        print("错误详情:")
        for error in result['errors']:
            print(f"  行{error['row']}, 字段{error['field']}: {error['message']}")

def test_import_data():
    """测试数据导入功能"""
    print("\n" + "=" * 80)
    print("测试通用导入服务 - 数据导入")
    print("=" * 80)
    
    service = UniversalImportService()
    
    # 测试数据
    data = [
        {'姓名': '张三', '性别': '男', '出生日期': '2001/1/1', '年龄': '25'},
        {'姓名': '李四', '性别': '女', '出生日期': '2001/01/15', '年龄': '26'},
    ]
    
    field_configs = [
        {'source_field': '姓名', 'target_field': 'name', 'data_type': 'VARCHAR', 'length': 50},
        {'source_field': '性别', 'target_field': 'gender', 'data_type': 'VARCHAR', 'length': 10},
        {'source_field': '出生日期', 'target_field': 'birth_date', 'data_type': 'DATE'},
        {'source_field': '年龄', 'target_field': 'age', 'data_type': 'INTEGER'},
    ]
    
    # 导入数据
    result = service.import_data(
        table_name='test_import_table',
        field_configs=field_configs,
        data=data,
        table_type='master'
    )
    
    print(f"\n导入结果:")
    print(f"成功: {result['success']}")
    print(f"插入条数: {result['inserted']}")
    if result['errors']:
        print(f"错误: {result['errors']}")

if __name__ == "__main__":
    try:
        test_analyze_file()
        test_validate_data()
        test_import_data()
        
        print("\n" + "=" * 80)
        print("所有测试完成!")
        print("=" * 80)
    except Exception as e:
        print(f"\n测试失败: {e}")
        import traceback
        traceback.print_exc()
