"""
检查模板文件中的实际占位符格式
"""
import re

# 读取模板文件
template_path = r'd:\erp_thirteen\tp_education_system\backend\templates\枣阳市机关事业单位养老保险改革过渡期内职务升降退休人员信息申报表htm.htm'

try:
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
except:
    try:
        with open(template_path, 'r', encoding='gbk') as f:
            content = f.read()
    except:
        with open(template_path, 'r', encoding='gb2312') as f:
            content = f.read()

# 提取所有 {{占位符}}
pattern = r'\{\{([^}]+)\}\}'
matches = re.findall(pattern, content)

print(f'从模板文件中提取的占位符（前10个）:')
for i, match in enumerate(matches[:10]):
    print(f'  {i+1}. {{{{{match}}}}}')  # 显示为 {{xxx}}

print(f'\n总共找到 {len(matches)} 个占位符')
