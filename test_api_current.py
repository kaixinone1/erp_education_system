"""
测试当前API调用
"""
import requests

# 测试 fill-data API
template_id = '枣阳市机关事业单位养老保险改革过渡期内职务升降退休人员信息申报表htm'
teacher_id = 293

# URL编码
template_id_encoded = requests.utils.quote(template_id)
url = f'http://localhost:8000/api/template-field-mapping/fill-data/{template_id_encoded}?teacher_id={teacher_id}'

print(f'模板ID: {template_id}')
print(f'编码后: {template_id_encoded}')
print(f'请求URL: {url}')

try:
    response = requests.get(url, timeout=10)
    print(f'状态码: {response.status_code}')
    result = response.json()
    print(f'响应状态: {result.get("status")}')
    print(f'响应消息: {result.get("message")}')
    print(f'数据键数: {len(result.get("data", {}))}')
    
    if result.get('unmapped_placeholders'):
        print(f'未映射占位符: {len(result["unmapped_placeholders"])}个')
        print(f'前5个: {result["unmapped_placeholders"][:5]}')
    
    # 打印前几个数据
    data = result.get('data', {})
    if data:
        print('\n前5个字段数据:')
        for i, (key, value) in enumerate(list(data.items())[:5]):
            print(f'  {key}: {value}')
    
except Exception as e:
    print(f'请求失败: {e}')
