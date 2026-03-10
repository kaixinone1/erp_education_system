import requests

# 测试1: 获取模板列表
print("=== 测试1: 获取模板列表 ===")
r = requests.get('http://localhost:8000/api/universal-templates/list')
print(f"Status: {r.status_code}")
print(f"Response: {r.text[:300]}")

# 测试2: 获取字段映射
print("\n=== 测试2: 获取字段映射 ===")
r = requests.get('http://localhost:8000/api/universal-templates/field-mappings')
print(f"Status: {r.status_code}")
print(f"Response: {r.text[:300]}")
