import requests

response = requests.get("http://localhost:8001/api/universal-template/preview/tpl_55b4ae00")
data = response.json()
metadata = data['数据']['metadata']

print("=" * 80)
print("           完整单元格元数据报告")