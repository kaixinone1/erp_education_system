#!/usr/bin/env python3
"""
测试文件解析API
"""

import requests
import pandas as pd
import io

BASE_URL = "http://localhost:8000"

def test_parse_file():
    """测试文件解析"""
    
    print("=" * 80)
    print("测试文件解析API")
    print("=" * 80)
    
    # 创建测试Excel文件
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
    
    url = f"{BASE_URL}/api/import/parse-file"
    print(f"URL: {url}")
    
    try:
        files = {'file': ('test_import.xlsx', excel_buffer, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
        params = {'preview_only': 'false'}
        response = requests.post(url, files=files, params=params, timeout=30)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"解析成功!")
            print(f"响应: {result}")
        else:
            print(f"错误: {response.text[:500]}")
    except Exception as e:
        print(f"请求失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_parse_file()
