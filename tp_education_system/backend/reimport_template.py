import requests

url = "http://localhost:8001/api/universal-template/import"
file_path = "d:/erp_thirteen/tp_education_system/backend/uploads/templates/义务教育学校教职工绩效工资审批表.xlsx"

with open(file_path, 'rb') as f:
    files = {'file': ('义务教育学校教职工绩效工资审批表.xlsx', f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
    data = {
        '模板名称': '义务教育学校教职工绩效工资审批表',
        '模板类型': '审批表'
    }
    response = requests.post(url, files=files, data=data)
    
print(f"状态码: {response.status_code}")
print(f"响应: {response.content.decode('utf-8')}")
