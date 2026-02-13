#!/usr/bin/env python3
"""
直接测试后端API返回的数据
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_api():
    """测试API"""
    
    print("=" * 80)
    print("测试后端API")
    print("=" * 80)
    
    # 获取数据
    print("\n获取数据...")
    try:
        response = requests.get(f"{BASE_URL}/api/data/teacher_log?page=1&page_size=5")
        print(f"状态码: {response.status_code}")
        print(f"响应内容:\n{json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    except Exception as e:
        print(f"获取数据失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_api()
