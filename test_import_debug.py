#!/usr/bin/env python3
"""
测试导入过程，查看详细日志
"""

import requests
import json

# 测试导入教师学历记录
url = "http://127.0.0.1:8000/api/import/finalize"

# 使用真实存在于 teacher_basic 表中的身份证号码
# 从查询结果看，真实的身份证号码如: 341203199612261536

# 模拟导入数据
test_data = {
    "table_name": "teacher_record",
    "field_configs": [
        {"sourceField": "姓名", "targetField": "姓名", "dataType": "VARCHAR", "length": 255},
        {"sourceField": "身份证号码", "targetField": "身份证号码", "dataType": "VARCHAR", "length": 255},
        {"sourceField": "学历类型", "targetField": "学历类型", "dataType": "VARCHAR", "length": 255},
        {"sourceField": "学历", "targetField": "学历", "dataType": "VARCHAR", "length": 255},
        {"sourceField": "学位", "targetField": "学位", "dataType": "VARCHAR", "length": 255},
        {"sourceField": "毕业院校", "targetField": "毕业院校", "dataType": "VARCHAR", "length": 255},
        {"sourceField": "专业", "targetField": "专业", "dataType": "VARCHAR", "length": 255},
        {"sourceField": "毕业日期", "targetField": "毕业日期", "dataType": "DATE"}
    ],
    "data": [
        {
            "姓名": "测试教师",
            "身份证号码": "341203199612261536",  # 使用真实存在的身份证号码
            "学历类型": "普通高等教育",
            "学历": "本科",
            "学位": "学士",
            "毕业院校": "北京大学",
            "专业": "计算机科学",
            "毕业日期": "2012-07-01"
        }
    ],
    "module_id": "module-1769848858485",
    "module_name": "人事管理",
    "file_name": "教师学历记录.xlsx",
    "chinese_title": "教师学历记录",
    "sub_module_id": "module-1769848871781",
    "sub_module_name": "教师管理",
    "table_type": "child",
    "parent_table": "teacher_basic"
}

print("测试导入教师学历记录...")
print("=" * 60)
print(f"表名: {test_data['table_name']}")
print(f"中文标题: {test_data['chinese_title']}")
print(f"表类型: {test_data['table_type']}")
print(f"父表: {test_data['parent_table']}")
print(f"数据条数: {len(test_data['data'])}")
print(f"身份证号码: {test_data['data'][0]['身份证号码']}")
print("=" * 60)

try:
    response = requests.post(url, json=test_data)
    print(f"\n响应状态: {response.status_code}")
    print(f"响应内容:")
    result = response.json()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    if result.get('record_count', 0) > 0:
        print(f"\n✓ 导入成功！插入了 {result['record_count']} 条数据")
    else:
        print(f"\n✗ 导入失败或未插入数据")
        if 'errors' in result:
            print(f"错误信息:")
            for error in result['errors']:
                print(f"  - {error}")
except Exception as e:
    print(f"请求失败: {e}")
