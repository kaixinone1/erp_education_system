"""
调试占位符提取 - 详细版本
"""
import re
from html.parser import HTMLParser
import os

file_path = r'd:\erp_thirteen\tp_education_system\backend\templates\枣阳市机关事业单位养老保险改革过渡期内职务升降退休人员信息申报表htm.htm'

print(f'文件路径: {file_path}')
print(f'文件存在: {os.path.exists(file_path)}')

# 尝试读取文件
content = None
for encoding in ['utf-8', 'gbk', 'gb2312', 'gb18030', 'latin-1']:
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            content = f.read()
        print(f'成功使用编码: {encoding}')
        break
    except UnicodeDecodeError as e:
        print(f'编码 {encoding} 失败: {e}')
        continue

if not content:
    print('无法读取文件内容！')
else:
    print(f'文件内容长度: {len(content)}')
    print(f'文件内容前200字符:\n{content[:200]}')
    print(f'\n{"="*60}\n')
    
    # 查找所有 {{...}}
    pattern = r'\{\{([^}]+)\}\}'
    matches = re.findall(pattern, content)
    print(f'正则表达式找到 {len(matches)} 个匹配')
    
    if matches:
        print(f'\n前3个原始匹配:')
        for i, match in enumerate(matches[:3]):
            print(f'  {i+1}. 长度={len(match)}, 内容={match[:100]}...')
        
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
        
        print(f'\n清理后的占位符:')
        cleaned = []
        for match in matches[:5]:
            clean_text = strip_tags(match).strip()
            clean_text = re.sub(r'\s+', '', clean_text)
            print(f'  原始: {match[:50]}...')
            print(f'  清理后: "{clean_text}"')
            
            # 验证
            if re.match(r'^[\w\u4e00-\u9fa5]+$', clean_text):
                print(f'  -> 验证通过')
                cleaned.append(clean_text)
            else:
                print(f'  -> 验证失败')
        
        print(f'\n最终有效占位符数: {len(cleaned)}')
