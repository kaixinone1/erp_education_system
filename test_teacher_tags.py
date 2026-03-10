import requests

# 测试获取教师标签 API
r = requests.get('http://localhost:8000/api/tag-relations/teacher/1/tags')
print(f'Status: {r.status_code}')
print(f'Response: {r.text}')
