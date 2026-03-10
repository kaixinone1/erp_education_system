import requests

url = 'http://localhost:8000/api/navigation-admin/tree'

try:
    response = requests.get(url, timeout=5)
    print(f'状态码: {response.status_code}')
    if response.status_code == 200:
        data = response.json()
        print(f'返回数据: {data}')
        if 'modules' in data:
            print(f'模块数量: {len(data["modules"])}')
            for m in data['modules']:
                print(f'  - {m.get("title", "无标题")}')
    else:
        print(f'错误: {response.text}')
except Exception as e:
    print(f'请求失败: {e}')
