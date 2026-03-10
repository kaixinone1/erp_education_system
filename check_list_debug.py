"""
调试业务清单API
"""
import requests

# 不带参数
url1 = 'http://localhost:8000/api/auto-table/retirement_report_data/list'
print(f'测试1: {url1}')
try:
    response = requests.get(url1, timeout=10)
    result = response.json()
    print(f'  状态: {result.get("status")}')
    print(f'  数据条数: {len(result.get("items", []))}')
    if result.get("message"):
        print(f'  消息: {result.get("message")}')
except Exception as e:
    print(f'  失败: {e}')

# 带参数
url2 = 'http://localhost:8000/api/auto-table/retirement_report_data/list?page=1&pageSize=10'
print(f'\n测试2: {url2}')
try:
    response = requests.get(url2, timeout=10)
    result = response.json()
    print(f'  状态: {result.get("status")}')
    print(f'  数据条数: {len(result.get("items", []))}')
    print(f'  总条数: {result.get("total")}')
    if result.get("message"):
        print(f'  消息: {result.get("message")}')
except Exception as e:
    print(f'  失败: {e}')

# 直接查询中间表数据
url3 = 'http://localhost:8000/api/intermediate/retirement_report_data?page=1&pageSize=10'
print(f'\n测试3: {url3}')
try:
    response = requests.get(url3, timeout=10)
    result = response.json()
    print(f'  状态: {result.get("status")}')
    print(f'  数据条数: {len(result.get("data", []))}')
    if result.get("message"):
        print(f'  消息: {result.get("message")}')
except Exception as e:
    print(f'  失败: {e}')
