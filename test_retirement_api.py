#!/usr/bin/env python3
"""测试退休呈报表API"""
import requests

BASE_URL = "http://localhost:8000"

def test_teacher_info():
    """测试获取教师信息"""
    try:
        response = requests.get(
            f"{BASE_URL}/api/retirement/teacher-info",
            params={"teacher_name": "王军峰"}
        )
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text[:500]}")
        return response.status_code == 200
    except Exception as e:
        print(f"请求失败: {e}")
        return False

def test_search_by_name():
    """测试搜索教师"""
    try:
        response = requests.get(
            f"{BASE_URL}/api/retirement/search-by-name",
            params={"name": "王军峰"}
        )
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text[:500]}")
        return response.status_code == 200
    except Exception as e:
        print(f"请求失败: {e}")
        return False

if __name__ == '__main__':
    print("测试获取教师信息...")
    test_teacher_info()
    print("\n测试搜索教师...")
    test_search_by_name()
