"""
测试任职状态选项API
"""
import requests

try:
    res = requests.get('http://localhost:8000/api/checklist-template/employment-status-options')
    result = res.json()
    print("API返回结果:")
    print(result)
except Exception as e:
    print(f"请求失败: {e}")
