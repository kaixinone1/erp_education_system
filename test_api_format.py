import requests

# 测试返回数据格式
print("=== 测试各API返回格式 ===\n")

# 1. 待办列表
r = requests.get('http://localhost:8000/api/todo-work/list')
print(f"待办列表: status={r.status_code}")
if r.status_code == 200:
    data = r.json()
    print(f"  keys: {data.keys()}")
    print(f"  data 数量: {len(data.get('data', []))}")

# 2. 模板列表
r = requests.get('http://localhost:8000/api/template-field-mapping/intermediate-tables')
print(f"\n模板列表: status={r.status_code}")
if r.status_code == 200:
    data = r.json()
    print(f"  keys: {data.keys()}")

# 3. 清单模板
r = requests.get('http://localhost:8000/api/checklist-template/list')
print(f"\n清单模板: status={r.status_code}")
if r.status_code == 200:
    data = r.json()
    print(f"  keys: {data.keys()}")
    print(f"  data 数量: {len(data.get('data', []))}")
