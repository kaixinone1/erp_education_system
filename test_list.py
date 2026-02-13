#!/usr/bin/env python3
"""测试模板列表API"""
import requests

url = "http://localhost:8000/api/templates/list"

try:
    response = requests.get(url)
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"状态: {result.get('status')}")
        templates = result.get('templates', [])
        print(f"模板数量: {len(templates)}")
        for t in templates:
            print(f"\n模板ID: {t.get('template_id')}")
            print(f"  名称: {t.get('template_name')}")
            print(f"  文件名: {t.get('file_name')}")
            print(f"  文件路径: {t.get('file_path')}")
    else:
        print(f"错误: {response.text}")
except Exception as e:
    print(f"错误: {e}")
