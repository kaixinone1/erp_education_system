import requests

# 测试模板列表 API
r = requests.get('http://localhost:8000/api/templates/list')
data = r.json()

print(f'Status: {r.status_code}')
print(f'Templates count: {len(data.get("templates", []))}')

if data.get('templates'):
    print('\n前3个模板:')
    for t in data['templates'][:3]:
        print(f'  id: {t.get("id")}')
        print(f'  template_id: {t.get("template_id")}')
        print(f'  template_name: {t.get("template_name")}')
        print()
