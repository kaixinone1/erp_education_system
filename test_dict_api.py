import requests

# 测试 dict_dictionary 表的字段 API
r = requests.get('http://localhost:8000/api/table-structure/dict_dictionary')
data = r.json()

print(f'表中文名: {data.get("chinese_name")}')
print('\n字段列表:')
for col in data.get('columns', []):
    print(f'  {col.get("name")} -> {col.get("chinese_name")}')
