"""
测试 teacher_id 参数
"""
import requests
from urllib.parse import quote

# 测试不同 teacher_id
template_id = '枣阳市机关事业单位养老保险改革过渡期内职务升降退休人员信息申报表htm'
encoded_template = quote(template_id)

for teacher_id in [0, 293, '293', None]:
    url = f'http://localhost:8000/api/template-field-mapping/fill-data/{encoded_template}?teacher_id={teacher_id}'
    print(f'\n测试 teacher_id={teacher_id} (类型: {type(teacher_id).__name__})')
    print(f'URL: {url}')
    
    try:
        response = requests.get(url, timeout=10)
        result = response.json()
        print(f'状态: {result.get("status")}')
        print(f'数据键数: {len(result.get("data", {}))}')
        if result.get("message"):
            print(f'消息: {result.get("message")}')
    except Exception as e:
        print(f'请求失败: {e}')
