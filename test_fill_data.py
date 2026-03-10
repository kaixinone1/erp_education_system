"""
测试 fill-data API
"""
import requests

# 测试 fill-data API
template_id = '职工退休呈报表html'
teacher_id = 273
url = f'http://localhost:8000/api/template-field-mapping/fill-data/{template_id}?teacher_id={teacher_id}'

try:
    print(f'请求URL: {url}')
    response = requests.get(url, timeout=10)
    print(f'状态码: {response.status_code}')
    result = response.json()
    print(f'响应状态: {result.get("status")}')
    print(f'响应消息: {result.get("message")}')
    print(f'数据键数: {len(result.get("data", {}))}')
    if result.get("unmapped_placeholders"):
        print(f'未映射占位符: {result["unmapped_placeholders"][:5]}')
except Exception as e:
    print(f'请求失败: {e}')
