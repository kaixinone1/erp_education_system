import requests

# 测试更新 API - 修改第一条记录的 employment_status
test_data = {
    "employment_status": "在职测试",
    "status_code": "zg_test",
    "sort_order_sequence": "99",
    "shi_fou_you_xiao": "是"
}

# 更新字典表
r = requests.put(
    'http://localhost:8000/api/data/dict_dictionary/1',
    json=test_data
)

print(f'更新状态: {r.status_code}')
print(f'响应: {r.text}')

# 验证更新
if r.status_code == 200:
    r2 = requests.get('http://localhost:8000/api/data/dict_dictionary')
    data = r2.json()
    print('\n验证 - 第一条记录:')
    if data.get('data'):
        print(f'  {data["data"][0]}')
