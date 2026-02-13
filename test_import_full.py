#!/usr/bin/env python3
"""
完整测试导入流程
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_full_import_flow():
    """测试完整导入流程"""
    
    print("=" * 80)
    print("完整导入流程测试")
    print("=" * 80)
    
    # 1. 测试文件上传解析
    print("\n1. 测试文件上传解析")
    print("-" * 80)
    
    # 创建一个测试Excel文件
    import pandas as pd
    import io
    
    # 创建测试数据
    test_data = {
        '姓名': ['张三', '李四', '王五'],
        '身份证号码': ['110101199001011234', '110101199001021235', '110101199001031236'],
        '学历': ['本科', '硕士', '博士'],
        '毕业院校': ['北京大学', '清华大学', '复旦大学']
    }
    df = pd.DataFrame(test_data)
    
    # 保存到内存
    excel_buffer = io.BytesIO()
    df.to_excel(excel_buffer, index=False, engine='openpyxl')
    excel_buffer.seek(0)
    
    url = f"{BASE_URL}/api/import/parse-excel"
    print(f"URL: {url}")
    
    try:
        files = {'file': ('test_import.xlsx', excel_buffer, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
        response = requests.post(url, files=files, timeout=30)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"解析成功!")
            print(f"数据行数: {result.get('total_rows', 0)}")
            print(f"列名: {result.get('columns', [])}")
            print(f"数据预览: {json.dumps(result.get('preview', [])[:2], ensure_ascii=False, indent=2)}")
        else:
            print(f"错误: {response.text[:500]}")
    except Exception as e:
        print(f"请求失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_full_import_flow()
