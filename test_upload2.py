#!/usr/bin/env python3
"""测试上传API - 新模板"""
import requests

# 测试上传
url = "http://localhost:8000/api/templates/upload"

# 准备表单数据 - 使用新的模板ID
import time
template_id = f"test_template_{int(time.time())}"

try:
    files = {
        'file': ('职工退休申报表.pdf', open(r'd:\erp_thirteen\tp_education_system\backend\templates\职工退休申报表.pdf', 'rb'), 'application/pdf')
    }
    data = {
        'template_id': template_id,
        'template_name': '测试模板2',
        'description': '测试上传功能'
    }
    
    response = requests.post(url, files=files, data=data)
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.text}")
except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()
