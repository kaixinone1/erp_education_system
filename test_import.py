#!/usr/bin/env python3
"""
测试导入功能
"""

import requests

BASE_URL = "http://localhost:8000"

def test_import():
    """测试导入API"""
    # 测试获取表结构
    print("=" * 80)
    print("测试获取表结构")
    print("=" * 80)
    
    url = f"{BASE_URL}/api/import/schema/teacher_basic"
    print(f"URL: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"表名: {result.get('name', 'N/A')}")
            print(f"字段数: {len(result.get('fields', []))}")
            return True
        else:
            print(f"错误: {response.text}")
            return False
    except Exception as e:
        print(f"请求失败: {e}")
        return False

if __name__ == "__main__":
    test_import()
