import requests

# 测试新增 API
test_data = {
    "employment_status": "新状态",
    "status_code": "xs",
    "sort_order_sequence": "10",
    "shi_fou_you_xiao": "是"
}

# 新增字典记录
r = requests.post(
    'http://localhost:8000/api/data/dict_dictionary',
    json=test_data
)

print(f'新增状态: {r.status_code}')
print(f'响应: {r.text}')

# 验证新增
if r.status_code == 200:
    r2 = requests.get('http://localhost:8000/api/data/dict_dictionary')
    data = r2.json()
    print(f'\n字典表记录总数: {len(data.get("data", []))}')
    print('最新记录:')
    for item in data.get('data', [])[-3:]:
        print(f'  {item}')
