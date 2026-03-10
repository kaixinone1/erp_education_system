"""
测试系统核心功能
"""
import requests
from urllib.parse import quote

print("=" * 60)
print("测试系统核心功能")
print("=" * 60)

# 1. 测试后端服务器
print("\n1. 测试后端服务器...")
try:
    r = requests.get("http://localhost:8000/", timeout=5)
    print(f"   ✓ 后端正常: {r.json()}")
except Exception as e:
    print(f"   ✗ 后端异常: {e}")

# 2. 测试业务清单API
print("\n2. 测试业务清单API...")
try:
    r = requests.get("http://localhost:8000/api/auto-table/retirement_report_data/list?page=1&pageSize=10", timeout=5)
    result = r.json()
    print(f"   状态: {result.get('status')}")
    print(f"   数据条数: {len(result.get('data', []))}")
    print(f"   总数: {result.get('total')}")
except Exception as e:
    print(f"   ✗ 异常: {e}")

# 3. 测试报表填报API
print("\n3. 测试报表填报API...")
template_id = '枣阳市机关事业单位养老保险改革过渡期内职务升降退休人员信息申报表htm'
encoded = quote(template_id)
try:
    r = requests.get(f"http://localhost:8000/api/template-field-mapping/fill-data/{encoded}?teacher_id=293", timeout=5)
    result = r.json()
    print(f"   状态: {result.get('status')}")
    print(f"   数据键数: {len(result.get('data', {}))}")
    if result.get('data'):
        data = result['data']
        print(f"   前3条数据: {list(data.items())[:3]}")
except Exception as e:
    print(f"   ✗ 异常: {e}")

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)
