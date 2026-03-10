"""
检查模板文件中的占位符格式
"""
import re

file_path = r'd:\erp_thirteen\tp_education_system\backend\templates\枣阳市机关事业单位养老保险改革过渡期内职务升降退休人员信息申报表htm.htm'

# 读取文件
try:
    with open(file_path, 'r', encoding='gbk') as f:
        content = f.read()
except:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

# 查找所有 {{...}}
pattern = r'\{\{([^}]+)\}\}'
matches = re.findall(pattern, content)

print(f'找到 {len(matches)} 个占位符')
print('\n前5个占位符的原始格式:')
for i, match in enumerate(matches[:5]):
    print(f'  {i+1}. {{{{{match}}}}}')

# 检查前端的正则是否能匹配
frontend_pattern = r'\{\{([\u4e00-\u9fa5a-zA-Z0-9_]+)\}\}'
frontend_matches = re.findall(frontend_pattern, content)
print(f'\n前端正则能匹配: {len(frontend_matches)} 个')

if frontend_matches:
    print('前5个:', frontend_matches[:5])
