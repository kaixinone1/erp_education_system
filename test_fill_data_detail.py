"""
测试 fill-data API，查看返回的数据详情
"""
import requests

# 测试 fill-data API
template_id = '职工退休呈报表html'
teacher_id = 273
url = f'http://localhost:8000/api/template-field-mapping/fill-data/{template_id}?teacher_id={teacher_id}'

try:
    response = requests.get(url, timeout=10)
    result = response.json()
    
    if result.get('status') == 'success':
        data = result.get('data', {})
        print(f'获取到 {len(data)} 个字段的数据')
        print('\n前10个字段及其值:')
        for i, (key, value) in enumerate(list(data.items())[:10]):
            print(f'  {key}: {value}')
    else:
        print(f'API返回错误: {result.get("message")}')
        if result.get('unmapped_placeholders'):
            print(f'未映射占位符数: {len(result["unmapped_placeholders"])}')
except Exception as e:
    print(f'请求失败: {e}')
