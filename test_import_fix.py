#!/usr/bin/env python3
"""
测试导入功能修复是否有效
"""

import json
import requests

# 后端API基础URL
BASE_URL = 'http://127.0.0.1:8000'

# 测试数据 - 匹配teacher_record表的实际结构
test_data = {
    "table_name": "teacher_record",
    "field_configs": [
        {
            "sourceField": "姓名",
            "targetField": "姓名",
            "dataType": "VARCHAR",
            "length": 255
        },
        {
            "sourceField": "身份证号码",
            "targetField": "身份证号码",
            "dataType": "VARCHAR",
            "length": 255
        },
        {
            "sourceField": "学历类型",
            "targetField": "学历类型",
            "dataType": "VARCHAR",
            "length": 255
        },
        {
            "sourceField": "学历",
            "targetField": "学历",
            "dataType": "VARCHAR",
            "length": 255
        },
        {
            "sourceField": "学位",
            "targetField": "学位",
            "dataType": "VARCHAR",
            "length": 255
        },
        {
            "sourceField": "毕业院校",
            "targetField": "毕业院校",
            "dataType": "VARCHAR",
            "length": 255
        },
        {
            "sourceField": "专业",
            "targetField": "专业",
            "dataType": "VARCHAR",
            "length": 255
        },
        {
            "sourceField": "毕业日期",
            "targetField": "毕业日期",
            "dataType": "DATE"
        }
    ],
    "data": [
        {
            "姓名": "张三",
            "身份证号码": "110101199001011234",
            "学历类型": "普通高等教育",
            "学历": "本科",
            "学位": "学士",
            "毕业院校": "北京大学",
            "专业": "计算机科学与技术",
            "毕业日期": "2012-06-30"
        },
        {
            "姓名": "李四",
            "身份证号码": "110101199102022345",
            "学历类型": "普通高等教育",
            "学历": "硕士",
            "学位": "硕士",
            "毕业院校": "清华大学",
            "专业": "软件工程",
            "毕业日期": "2015-06-30"
        },
        {
            "姓名": "王五",
            "身份证号码": "110101199203033456",
            "学历类型": "普通高等教育",
            "学历": "博士",
            "学位": "博士",
            "毕业院校": "中国科学院",
            "专业": "人工智能",
            "毕业日期": "2018-06-30"
        }
    ],
    "module_id": "teacher",
    "module_name": "教师管理",
    "table_type": "master",
    "file_name": "教师记录.xlsx",
    "chinese_title": "教师记录"
}

def test_import():
    """测试导入功能"""
    print("开始测试导入功能...")
    
    try:
        # 调用导入API
        response = requests.post(
            f"{BASE_URL}/api/import/finalize",
            headers={"Content-Type": "application/json"},
            data=json.dumps(test_data)
        )
        
        print(f"API响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"导入结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
            
            if result.get("status") in ["success", "partial_success"]:
                print("✓ 导入成功！")
                print(f"导入记录数: {result.get('record_count', 0)}")
                
                if "errors" in result:
                    print(f"⚠️  存在错误: {len(result['errors'])} 个")
                    for error in result['errors']:
                        print(f"  - {error}")
            else:
                print("✗ 导入失败！")
        else:
            print(f"✗ API调用失败: {response.text}")
            
    except Exception as e:
        print(f"✗ 测试过程中发生错误: {e}")

def test_table_existence():
    """测试表是否存在"""
    print("\n测试表是否存在...")
    
    try:
        # 调用数据API查看表数据
        response = requests.get(
            f"{BASE_URL}/api/data/teacher_record",
            params={"page": 1, "page_size": 10}
        )
        
        print(f"API响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"表数据: {json.dumps(result, ensure_ascii=False, indent=2)}")
            print(f"总记录数: {result.get('total', 0)}")
            print("✓ 表存在且可以访问！")
        else:
            print(f"✗ 表可能不存在或无法访问: {response.text}")
            
    except Exception as e:
        print(f"✗ 测试过程中发生错误: {e}")

if __name__ == "__main__":
    print("=== 测试导入功能修复 ===")
    test_import()
    test_table_existence()
    print("\n=== 测试完成 ===")
