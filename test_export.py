import requests

# 测试导出Word
url = "http://localhost:8000/api/templates/职工退休呈报表html/export-word"
data = {
    "teacher_id": "301",
    "data": {}
}

try:
    response = requests.post(url, json=data, timeout=30)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:500]}")
except Exception as e:
    print(f"Error: {e}")
