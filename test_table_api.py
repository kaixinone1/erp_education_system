import requests
r = requests.get('http://localhost:8000/api/table-structure/tables')
data = r.json()
print('Tables with Chinese names:')
for t in data.get('tables', [])[:10]:
    print(f'  {t["name"]}: chinese={t["chinese_name"]}, has_chinese={t["has_chinese_name"]}')
