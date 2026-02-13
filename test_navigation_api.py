#!/usr/bin/env python3
import requests

try:
    response = requests.get('http://localhost:8000/api/navigation-admin/tree')
    if response.status_code == 200:
        data = response.json()
        print("API返回成功！")
        print(f"模块数量: {len(data.get('modules', []))}")
        
        # 查找报表管理模块
        for module in data.get('modules', []):
            if module.get('title') == '报表管理':
                print(f"\n找到报表管理模块:")
                print(f"  子节点数量: {len(module.get('children', []))}")
                for child in module.get('children', []):
                    print(f"    - {child.get('title')} ({child.get('type')})")
                    if child.get('children'):
                        for grandchild in child.get('children', []):
                            print(f"      - {grandchild.get('title')}")
    else:
        print(f"API返回错误: {response.status_code}")
except Exception as e:
    print(f"请求失败: {e}")
