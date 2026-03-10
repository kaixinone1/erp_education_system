import requests

# 测试各个API
apis = [
    ('/api/todo-work/list', '待办列表'),
    ('/api/template-field-mapping/intermediate-tables', '模板列表'),
    ('/api/checklist-template/list', '清单模板'),
]

for api, name in apis:
    try:
        r = requests.get(f'http://localhost:8000{api}', timeout=3)
        print(f'{name}: {r.status_code}')
        if r.status_code != 200:
            print(f'  错误: {r.text[:200]}')
    except Exception as e:
        print(f'{name}: 失败 - {e}')
