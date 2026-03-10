import requests

# 测试字段 API
tables = ['teacher_basic_info', 'performance_pay_approval']

for table in tables:
    r = requests.get(f'http://localhost:8000/api/table-structure/{table}')
    data = r.json()
    print(f'\n表: {table}')
    print(f'中文名: {data.get("chinese_name")}')
    if data.get('columns'):
        print('前5个字段:')
        for col in data['columns'][:5]:
            print(f'  {col.get("name")}: {col.get("chinese_name", "无")}')
