import requests

# 测试导出
print("=== 测试导出：职务升降表 ===")
url = "http://localhost:8000/api/universal-templates/枣阳市机关事业单位养老保险改革过渡期内职务升降退休人员信息申报表/export"
params = {
    "teacher_id": 301,
    "teacher_name": "张三"
}

try:
    response = requests.post(url, params=params, timeout=30)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        # 保存文件
        content_disposition = response.headers.get('content-disposition', '')
        filename = 'test_export.docx'
        if 'filename=' in content_disposition:
            filename = content_disposition.split('filename=')[1].strip('"')
        
        with open(f'd:/erp_thirteen/{filename}', 'wb') as f:
            f.write(response.content)
        print(f"导出成功！文件保存为: {filename}")
    else:
        print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
