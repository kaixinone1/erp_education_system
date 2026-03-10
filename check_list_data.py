"""
检查业务清单返回的数据结构
"""
import requests

# 获取业务清单数据
url = 'http://localhost:8000/api/auto-table/retirement_report_data/list?page=1&pageSize=10'

try:
    response = requests.get(url, timeout=10)
    result = response.json()
    
    if result.get('status') == 'success':
        items = result.get('items', [])
        print(f'获取到 {len(items)} 条数据')
        
        if items:
            # 打印第一条数据的所有字段
            print('\n第一条数据的字段:')
            for key, value in items[0].items():
                print(f'  {key}: {value}')
        
        # 检查 teacher_id 字段
        teacher_ids = [item.get('teacher_id') for item in items]
        print(f'\nteacher_id 列表: {teacher_ids}')
    else:
        print(f'API返回错误: {result.get("message")}')
        
except Exception as e:
    print(f'请求失败: {e}')
