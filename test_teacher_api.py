import requests

# 测试搜索教师 API
r = requests.get('http://localhost:8000/api/data/teacher_basic_info?page=1&size=5&name=张')
print(f'Status: {r.status_code}')
print(f'Response: {r.text[:500]}')
