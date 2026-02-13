#!/usr/bin/env python3
"""
测试API返回的个人身份数据
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_api():
    """测试API"""
    
    print("=" * 80)
    print("测试教师个人身份API")
    print("=" * 80)
    
    # 获取数据
    print("\n获取数据...")
    try:
        response = requests.get(f"{BASE_URL}/api/data/teacher_personal_identity?page=1&page_size=5")
        print(f"状态码: {response.status_code}")
        data = response.json()
        print(f"总条数: {data.get('total', 0)}")
        items = data.get('data', [])
        print(f"返回条数: {len(items)}")
        
        if items:
            print("\n前3条数据:")
            for i, item in enumerate(items[:3], 1):
                print(f"\n  记录{i}:")
                for key, value in item.items():
                    print(f"    {key}: {value}")
        else:
            print("\n没有返回数据！")
            print(f"完整响应: {json.dumps(data, ensure_ascii=False, indent=2)[:500]}")
    except Exception as e:
        print(f"获取数据失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_api()
