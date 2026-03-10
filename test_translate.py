"""
测试翻译功能
"""
import requests

test_names = [
    "教师基础信息",
    "退休呈报数据",
    "教师专业技术资格",
    "退休呈报表",
    "教师工作业务数据"
]

for name in test_names:
    try:
        res = requests.post('http://localhost:8000/api/intermediate-table/translate-name', 
                          json={"name": name})
        result = res.json()
        print(f"{name} -> {result.get('data', result.get('message'))}")
    except Exception as e:
        print(f"{name} -> 错误: {e}")
