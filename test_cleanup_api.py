#!/usr/bin/env python3
"""
测试清理API
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_list_tables():
    """测试获取可删除表列表"""
    print("=" * 80)
    print("测试获取可删除表列表")
    print("=" * 80)
    
    try:
        response = requests.get(f"{BASE_URL}/api/admin/list-deletable-tables")
        print(f"状态码: {response.status_code}")
        
        if response.ok:
            result = response.json()
            print(f"\n可删除的表（显示中文名）：")
            for table in result.get('tables', []):
                status = "✓" if table['exists_in_db'] else "✗"
                print(f"  [{status}] {table['chinese_name']} ({table['english_name']}) - {table['table_type']}")
            print(f"\n总计: {result.get('count', 0)} 个表")
        else:
            print(f"请求失败: {response.text}")
    except Exception as e:
        print(f"请求异常: {e}")

def test_cleanup_table(chinese_name: str):
    """测试清理表"""
    print("\n" + "=" * 80)
    print(f"测试清理表: {chinese_name}")
    print("=" * 80)
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/admin/cleanup-table",
            json={"chinese_name": chinese_name}
        )
        print(f"状态码: {response.status_code}")
        
        result = response.json()
        print(f"\n结果:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as e:
        print(f"请求异常: {e}")

if __name__ == "__main__":
    # 先获取可删除表列表
    test_list_tables()
    
    # 测试清理（请替换为实际要删除的表名）
    # test_cleanup_table("教师人才类型")
