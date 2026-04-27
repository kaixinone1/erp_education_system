# 替换文件中的字段名
with open('d:\\erp_thirteen\\tp_education_system\\backend\\routes\\business_checklist_routes.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('清单截止天数', '截止日期')

with open('d:\\erp_thirteen\\tp_education_system\\backend\\routes\\business_checklist_routes.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("替换完成")
