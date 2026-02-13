#!/usr/bin/env python3
"""
测试搜索功能
"""

import requests

BASE_URL = "http://localhost:8000"

def test_search(table_name, keyword=""):
    """测试搜索功能"""
    url = f"{BASE_URL}/api/data/{table_name}"
    params = {
        "page": 1,
        "size": 20
    }
    if keyword:
        params["keyword"] = keyword
    
    print(f"\n测试表: {table_name}")
    print(f"搜索关键词: {keyword or '无'}")
    print(f"URL: {url}")
    print(f"参数: {params}")
    
    try:
        response = requests.get(url, params=params, timeout=10)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"总记录数: {result.get('total', 0)}")
            print(f"返回数据条数: {len(result.get('data', []))}")
            if result.get('data'):
                print(f"第一条数据: {result['data'][0]}")
            return True
        else:
            print(f"错误: {response.text}")
            return False
    except Exception as e:
        print(f"请求失败: {e}")
        return False

if __name__ == "__main__":
    # 测试教师基础信息表（应该能用）
    print("=" * 80)
    print("测试教师基础信息表")
    print("=" * 80)
    test_search("teacher_basic", "")
    test_search("teacher_basic", "李")
    
    # 测试教师学历记录表（应该现在能用）
    print("\n" + "=" * 80)
    print("测试教师学历记录表")
    print("=" * 80)
    test_search("teacher_record", "")
    test_search("teacher_record", "李")
    test_search("teacher_record", "本科")
