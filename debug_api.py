"""
直接测试 API，找出问题
"""
import requests
import json

# 测试两个模板
templates = [
    ('枣阳市机关事业单位养老保险改革过渡期内职务升降退休人员信息申报表htm', 293),
    ('职工退休呈报表html', 273)
]

for template_id, teacher_id in templates:
    print(f'\n{"="*60}')
    print(f'测试模板: {template_id}')
    print(f'教师ID: {teacher_id}')
    print(f'{"="*60}')
    
    # URL编码
    from urllib.parse import quote
    encoded_template = quote(template_id)
    url = f'http://localhost:8000/api/template-field-mapping/fill-data/{encoded_template}?teacher_id={teacher_id}'
    
    try:
        response = requests.get(url, timeout=10)
        result = response.json()
        
        print(f'状态码: {response.status_code}')
        print(f'API状态: {result.get("status")}')
        print(f'消息: {result.get("message")}')
        print(f'数据键数: {len(result.get("data", {}))}')
        
        if result.get('unmapped_placeholders'):
            print(f'未映射占位符: {len(result["unmapped_placeholders"])}个')
            print(f'前3个: {result["unmapped_placeholders"][:3]}')
        
        # 打印数据
        data = result.get('data', {})
        if data:
            print('\n前5个数据:')
            for i, (key, value) in enumerate(list(data.items())[:5]):
                print(f'  {key}: {value}')
        else:
            print('\n数据为空!')
            
    except Exception as e:
        print(f'请求失败: {e}')

print('\n\n测试完成')
