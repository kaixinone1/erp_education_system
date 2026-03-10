import requests

# 测试上传接口
url = 'http://localhost:8000/api/templates/upload'

# 准备测试数据
test_html = """
<!DOCTYPE html>
<html>
<head><title>测试模板</title></head>
<body>
    <h1>姓名: {{姓名}}</h1>
    <p>性别: {{性别}}</p>
</body>
</html>
"""

# 写入临时文件
with open('test_template.htm', 'w', encoding='utf-8') as f:
    f.write(test_html)

# 测试上传
with open('test_template.htm', 'rb') as f:
    files = {'file': ('test_template.htm', f, 'text/html')}
    data = {
        'template_id': 'test_2026',
        'template_name': '测试模板',
        'description': '测试'
    }
    r = requests.post(url, data=data, files=files)

print(f"Status: {r.status_code}")
print(f"Response: {r.text}")
