#!/usr/bin/env python3
"""
测试导入页面相关API
"""

import requests

BASE_URL = "http://localhost:8000"

def test_api():
    """测试导入相关API"""
    
    # 测试1: 获取schema mappings
    print("=" * 80)
    print("测试1: 获取schema mappings")
    print("=" * 80)
    url = f"{BASE_URL}/api/data/config/schema"
    print(f"URL: {url}")
    try:
        response = requests.get(url, timeout=10)
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"表数量: {len(result.get('tables', {}))}")
            print(f"字典表数量: {len(result.get('dictionaries', {}))}")
        else:
            print(f"错误: {response.text[:200]}")
    except Exception as e:
        print(f"请求失败: {e}")
    
    # 测试2: 获取表结构
    print("\n" + "=" * 80)
    print("测试2: 获取表结构")
    print("=" * 80)
    url = f"{BASE_URL}/api/data/schema/teacher_basic"
    print(f"URL: {url}")
    try:
        response = requests.get(url, timeout=10)
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"表名: {result.get('name', 'N/A')}")
            print(f"字段数: {len(result.get('fields', []))}")
        else:
            print(f"错误: {response.text[:200]}")
    except Exception as e:
        print(f"请求失败: {e}")
    
    # 测试3: 检查导入路由
    print("\n" + "=" * 80)
    print("测试3: 检查导入路由")
    print("=" * 80)
    url = f"{BASE_URL}/api/import/translate-table-name"
    print(f"URL: {url}")
    try:
        response = requests.post(url, json={"chinese_name": "测试", "module_name": "测试模块"}, timeout=10)
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"响应: {result}")
        else:
            print(f"错误: {response.text[:200]}")
    except Exception as e:
        print(f"请求失败: {e}")

if __name__ == "__main__":
    test_api()
