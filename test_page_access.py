#!/usr/bin/env python3
"""
测试页面访问
"""

import requests

BASE_URL = "http://localhost:5173"  # 前端开发服务器

def test_page():
    """测试页面访问"""
    
    # 测试导入页面
    print("=" * 80)
    print("测试导入页面访问")
    print("=" * 80)
    
    url = f"{BASE_URL}/import/workbench"
    print(f"URL: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        print(f"状态码: {response.status_code}")
        print(f"内容长度: {len(response.text)}")
        
        if response.status_code == 200:
            # 检查是否包含关键内容
            if "数据导入工作台" in response.text:
                print("✅ 页面内容正确，包含'数据导入工作台'")
            else:
                print("⚠️ 页面内容可能不正确，未找到'数据导入工作台'")
                # 打印部分内容
                print("页面内容前500字符:")
                print(response.text[:500])
        else:
            print(f"❌ 访问失败")
    except Exception as e:
        print(f"请求失败: {e}")

if __name__ == "__main__":
    test_page()
