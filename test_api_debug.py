#!/usr/bin/env python3
"""调试API"""
import requests
import urllib.parse

BASE_URL = "http://localhost:8000"

def test():
    # 测试不同的URL编码方式
    name = "王军锋"
    
    # 方式1: 直接传递
    url1 = f"{BASE_URL}/api/retirement/search-by-name?name={name}"
    print(f"方式1 URL: {url1}")
    response1 = requests.get(url1)
    print(f"方式1 状态: {response1.status_code}, 结果: {response1.json().get('count')}")
    
    # 方式2: URL编码
    url2 = f"{BASE_URL}/api/retirement/search-by-name?name={urllib.parse.quote(name)}"
    print(f"\n方式2 URL: {url2}")
    response2 = requests.get(url2)
    print(f"方式2 状态: {response2.status_code}, 结果: {response2.json().get('count')}")
    
    # 方式3: 使用params参数
    url3 = f"{BASE_URL}/api/retirement/search-by-name"
    print(f"\n方式3 URL: {url3}")
    response3 = requests.get(url3, params={"name": name})
    print(f"方式3 实际URL: {response3.request.url}")
    print(f"方式3 状态: {response3.status_code}, 结果: {response3.json().get('count')}")

if __name__ == '__main__':
    test()
