#!/usr/bin/env python3
import requests

# 测试API
url = 'http://localhost:8000/api/template-field-mapping/template-placeholders/16'
print(f"测试URL: {url}")

try:
    response = requests.get(url)
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {response.text[:500]}")
except Exception as e:
    print(f"错误: {e}")
