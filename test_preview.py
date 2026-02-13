#!/usr/bin/env python3
"""测试PDF预览API"""
import requests

# 测试预览API
template_id = "test_template_1770691934"  # 使用之前上传的模板ID
url = f"http://localhost:8000/api/templates/{template_id}/preview-pdf?page=1"

try:
    response = requests.get(url)
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"总页数: {result.get('total_pages')}")
        print(f"图片数据长度: {len(result.get('image', ''))}")
    else:
        print(f"错误: {response.text}")
except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()
