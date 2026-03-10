"""
测试报表页面URL
"""
import requests
from urllib.parse import quote

# 模拟前端跳转的URL
template_id = '枣阳市机关事业单位养老保险改革过渡期内职务升降退休人员信息申报表htm'
teacher_id = 273

encoded_template = quote(template_id)
url = f'http://localhost:5173/report-view/{encoded_template}/{teacher_id}'

print(f'报表页面URL: {url}')
print(f'\n请手动在浏览器中打开这个URL，检查是否能正常显示数据')

# 同时测试API
api_url = f'http://localhost:8000/api/template-field-mapping/fill-data/{encoded_template}?teacher_id={teacher_id}'
print(f'\nAPI URL: {api_url}')

try:
    response = requests.get(api_url, timeout=10)
    result = response.json()
    print(f'API状态: {result.get("status")}')
    print(f'数据键数: {len(result.get("data", {}))}')
except Exception as e:
    print(f'API请求失败: {e}')
