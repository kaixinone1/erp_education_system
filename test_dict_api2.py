import requests

# 测试字典 API
r = requests.get('http://localhost:8000/api/data/dict_dictionary')
print(f'Status: {r.status_code}')
if r.status_code == 200:
    data = r.json()
    print(f'Data count: {len(data.get("data", []))}')
    print(f'Data: {data.get("data", [])[:5]}')
else:
    print(f'Error: {r.text}')
