"""
测试API返回的数据结构
"""
import requests

url = 'http://localhost:8000/api/auto-table/retirement_report_data/list?page=1&pageSize=10'

try:
    response = requests.get(url, timeout=10)
    result = response.json()
    
    print('API返回的完整数据结构:')
    print(f'  status: {result.get("status")}')
    print(f'  total: {result.get("total")}')
    print(f'  page: {result.get("page")}')
    print(f'  page_size: {result.get("page_size")}')
    print(f'  data 类型: {type(result.get("data"))}')
    print(f'  data 长度: {len(result.get("data", []))}')
    
    if result.get("data"):
        print(f'\n第一条数据:')
        print(result["data"][0])
    
    # 检查是否有 items 字段
    if "items" in result:
        print(f'\n有 items 字段，长度: {len(result["items"])}')
    else:
        print(f'\n没有 items 字段')
        
except Exception as e:
    print(f'请求失败: {e}')
