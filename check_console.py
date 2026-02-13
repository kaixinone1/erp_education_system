#!/usr/bin/env python3
"""
检查导入页面加载情况
"""

import requests
import time

BASE_URL = "http://localhost:5173"
API_URL = "http://localhost:8000"

def check():
    print("=" * 80)
    print("检查导入页面")
    print("=" * 80)
    
    # 1. 检查前端服务
    try:
        response = requests.get(BASE_URL, timeout=5)
        print(f"✅ 前端服务正常: {response.status_code}")
    except Exception as e:
        print(f"❌ 前端服务异常: {e}")
        return
    
    # 2. 检查后端服务
    try:
        response = requests.get(f"{API_URL}/api/navigation-admin/tree", timeout=5)
        print(f"✅ 后端服务正常: {response.status_code}")
    except Exception as e:
        print(f"❌ 后端服务异常: {e}")
        return
    
    # 3. 检查导入API
    try:
        response = requests.get(f"{API_URL}/api/import/translate-table-name", timeout=5)
        print(f"✅ 导入API正常: {response.status_code}")
    except Exception as e:
        print(f"❌ 导入API异常: {e}")
    
    # 4. 直接访问导入页面URL
    try:
        response = requests.get(f"{BASE_URL}/import/workbench", timeout=5)
        print(f"✅ 导入页面URL可访问: {response.status_code}")
        
        # 检查返回的内容
        if "数据导入工作台" in response.text:
            print("✅ 页面包含'数据导入工作台'文本")
        else:
            print("⚠️ 页面不包含'数据导入工作台'文本")
            
        if "FileSelectionPanel" in response.text or "file-selection-panel" in response.text:
            print("✅ 页面包含文件选择面板组件")
        else:
            print("⚠️ 页面不包含文件选择面板组件")
            
    except Exception as e:
        print(f"❌ 导入页面访问异常: {e}")
    
    print("\n" + "=" * 80)
    print("诊断建议:")
    print("=" * 80)
    print("1. 请打开浏览器开发者工具(F12)")
    print("2. 切换到 Console(控制台) 标签")
    print("3. 点击'数据导入'菜单")
    print("4. 查看是否有红色错误信息")
    print("5. 切换到 Network(网络) 标签")
    print("6. 查看是否有请求失败(红色)")

if __name__ == "__main__":
    check()
