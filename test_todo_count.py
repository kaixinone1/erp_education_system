import requests

# 测试待办工作数量 API
r = requests.get('http://localhost:8000/api/todo-work/count')
print(f'Status: {r.status_code}')
print(f'Response: {r.text}')

# 也测试列表 API
r2 = requests.get('http://localhost:8000/api/todo-work/list')
print(f'\nList Status: {r2.status_code}')
data = r2.json()
print(f'Todo count from list: {len(data.get("todos", []))}')
