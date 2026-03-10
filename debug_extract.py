"""
调试占位符提取
"""
import re
from html.parser import HTMLParser

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

print(f'文件内容长度: {len(content)}')
print(f'文件内容前500字符:\n{content[:500]}')
print(f'\n{"="*60}\n')

# 提取所有 {{...}}
pattern = r'\{\{([^}]+)\}\}'
matches = re.findall(pattern, content)

print(f'提取到的原始匹配数: {len(matches)}')
print(f'\n前10个原始匹配:')
for i, match in enumerate(matches[:10]):
    print(f'  {i+1}. {{{{{match}}}}}')
    print(f'     长度: {len(match)}')
    print(f'     包含HTML标签: {"<" in match}')

print(f'\n{"="*60}\n')

# 清理HTML标签
class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    if not html:
        return ''
    s = MLStripper()
    try:
        s.feed(html)
        return s.get_data()
    except Exception as e:
        print(f"HTML解析失败: {e}")
        return re.sub(r'<[^>]+>', '', html)

cleaned = []
for match in matches[:10]:
    clean_text = strip_tags(match).strip()
    clean_text = re.sub(r'\s+', '', clean_text)
    print(f'清理后: "{clean_text}"')
    
    # 验证
    if re.match(r'^[\w\u4e00-\u9fa5]+$', clean_text):
        print(f'  -> 验证通过')
        cleaned.append(clean_text)
    else:
        print(f'  -> 验证失败')

print(f'\n清理后有效的占位符数: {len(cleaned)}')
