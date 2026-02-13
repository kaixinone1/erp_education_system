#!/usr/bin/env python3
import requests

# 测试不同的模板ID
test_ids = [16, "16", "职工退休申报表html"]

for tid in test_ids:
    url = f'http://localhost:8000/api/template-field-mapping/template-placeholders/{tid}'
    print(f"\n测试 URL: {url}")
    try:
        response = requests.get(url)
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"成功! 占位符数量: {len(data.get('placeholders', []))}")
        else:
            print(f"错误: {response.text[:200]}")
    except Exception as e:
        print(f"异常: {e}")
