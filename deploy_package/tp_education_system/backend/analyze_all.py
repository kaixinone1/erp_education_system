import requests
import json
resp = requests.get('http://localhost:8000/api/data/business_checklist')
data = resp.json()
for item in data.get('data', []):
    name = item.get('清单名称')
    tasks = item.get('任务项列表')
    print(f'=== {name} ===')
    if tasks:
        print(f'任务项数: {len(tasks)}')
        for t in tasks:
            print(f'  - 标题: {t.get("标题")}')
            print(f'    类型: {t.get("类型")}')
            print(f'    目标: {t.get("目标")}')
            print(f'    参数: {t.get("参数")}')
            print()
