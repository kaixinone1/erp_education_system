#!/usr/bin/env python3
"""测试上传API"""
import requests

# 测试上传
url = "http://localhost:8000/api/templates/upload"

# 准备表单数据
files = {
    'file': ('test.pdf', open(r'd:\erp_thirteen\tp_education_system\backend\templates\职工退休申报表.pdf', 'rb'), 'application/pdf')
}
data = {
    'template_id': 'test_template_001',
    'template_name': '测试模板',
    'description': '测试上传'
}

try:
    response = requests.post(url, files=files, data=data)
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
except Exception as e:
    print(f"错误: {e}")
