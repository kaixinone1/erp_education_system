"""
直接测试 API 是否可访问
"""
import requests

# 测试第二个模板
template_id = '职工退休呈报表html'
url = f'http://localhost:8000/api/template-field-mapping/template-placeholders/{template_id}'

try:
    print(f'请求URL: {url}')
    response = requests.get(url, timeout=10)
    print(f'状态码: {response.status_code}')
    print(f'响应内容前200字: {response.text[:200]}')
except Exception as e:
    print(f'请求失败: {e}')
