"""
最终测试 API
"""
import requests

# 测试 API 是否可访问
url = 'http://localhost:8000/api/template-field-mapping/template-placeholders/职工退休呈报表html'

try:
    print(f'请求URL: {url}')
    response = requests.get(url, timeout=10)
    print(f'状态码: {response.status_code}')
    print(f'响应内容: {response.text[:300]}')
except Exception as e:
    print(f'请求失败: {e}')
