#!/usr/bin/env python3
"""
测试表结构管理API
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_get_tables():
    """测试获取表列表"""
    print("=" * 80)
    print("测试获取表列表（表结构管理）")
    print("=" * 80)
    
    try:
        response = requests.get(f"{BASE_URL}/api/table-structure/tables")
        print(f"状态码: {response.status_code}")
        
        if response.ok:
            result = response.json()
            tables = result.get('tables', [])
            
            print(f"\n总计 {len(tables)} 个表:\n")
            
            # 按类型分组
            with_chinese = []
            without_chinese = []
            
            for table in tables:
                if table.get('has_chinese_name'):
                    with_chinese.append(table)
                else:
                    without_chinese.append(table)
            
            print(f"有中文名的表 ({len(with_chinese)} 个):")
            for table in with_chinese:
                print(f"  ✓ {table['chinese_name']} ({table['name']}) - {table['type']}")
            
            print(f"\n无中文名的表 ({len(without_chinese)} 个):")
            for table in without_chinese:
                print(f"  ✗ {table['name']} - {table['type']}")
        else:
            print(f"请求失败: {response.text}")
    except Exception as e:
        print(f"请求异常: {e}")

if __name__ == "__main__":
    test_get_tables()
