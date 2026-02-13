#!/usr/bin/env python3
"""
测试日期格式转换功能
"""

import requests
import pandas as pd
import io

BASE_URL = "http://localhost:8000"

def test_date_conversion():
    """测试日期格式转换"""
    
    print("=" * 80)
    print("测试日期格式自动转换")
    print("=" * 80)
    
    # 创建测试数据，包含各种日期格式
    test_data = {
        '姓名': ['张三', '李四', '王五'],
        '出生日期': ['2001/1/1', '2001/01/01', '2001-01-01'],  # 不同格式的日期
        '毕业日期': ['2001年1月1日', '2001年01月01日', '2001-1-1'],
        '学历': ['本科', '硕士', '博士']
    }
    df = pd.DataFrame(test_data)
    
    # 保存到内存
    excel_buffer = io.BytesIO()
    df.to_excel(excel_buffer, index=False, engine='openpyxl')
    excel_buffer.seek(0)
    
    url = f"{BASE_URL}/api/import/parse-file"
    print(f"\n上传文件到: {url}")
    print("原始数据:")
    print(df)
    
    try:
        files = {'file': ('test_date.xlsx', excel_buffer, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
        params = {'preview_only': 'true'}
        response = requests.post(url, files=files, params=params, timeout=30)
        
        print(f"\n状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("\n✅ 解析成功!")
            print(f"总数据行数: {result.get('total_rows', 0)}")
            print(f"字段: {result.get('fields', [])}")
            print("\n预览数据（日期应该已经被转换）:")
            for i, row in enumerate(result.get('preview_data', [])):
                print(f"  行{i+1}: {row}")
        else:
            print(f"❌ 错误: {response.text[:500]}")
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_date_conversion()
