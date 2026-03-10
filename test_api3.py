import requests

# 使用正确的模板ID（htm结尾）
url = 'http://localhost:8000/api/template-field-mapping/fill-data/枣阳市机关事业单位养老保险改革过渡期内职务升降退休人员信息申报表htm?teacher_id=293'

try:
    response = requests.get(url, timeout=10)
    print(f'状态码: {response.status_code}')
    if response.status_code != 200:
        print(f'错误: {response.text}')
    else:
        data = response.json()
        print(f'成功')
        print(f'数据: {data}')
except Exception as e:
    print(f'请求失败: {e}')
    import traceback
    traceback.print_exc()
