"""
测试 template-placeholders API，使用第一个模板
"""
import requests
import urllib.parse

# 测试第一个模板
template_id = '枣阳市机关事业单位养老保险改革过渡期内职务升降退休人员信息申报表htm'
encoded_id = urllib.parse.quote(template_id)
url = f'http://localhost:8000/api/template-field-mapping/template-placeholders/{encoded_id}'

try:
    print(f'模板ID: {template_id}')
    print(f'编码后: {encoded_id}')
    print(f'请求URL: {url}')
    response = requests.get(url, timeout=10)
    print(f'状态码: {response.status_code}')
    print(f'响应内容: {response.text[:500]}')
except Exception as e:
    print(f'请求失败: {e}')
