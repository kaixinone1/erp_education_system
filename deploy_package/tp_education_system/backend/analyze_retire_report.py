import requests
resp = requests.get('http://localhost:8000/api/data/business_checklist')
data = resp.json()
for item in data.get('data', []):
    if item.get('清单名称') == '退休教师呈报业务清单':
        print('=== 退休教师呈报业务清单 ===')
        tasks = item.get('任务项列表')
        if tasks:
            print(f'任务项数: {len(tasks)}')
            for t in tasks:
                print(f'---')
                print(f'序号: {t.get("序号")}')
                print(f'标题: {t.get("标题")}')
                print(f'类型: {t.get("类型")}')
                print(f'目标: {t.get("目标")}')
                print(f'参数: {t.get("参数")}')
