#!/usr/bin/env python3
"""
直接检查模板文件中的所有花括号内容
"""
import re
import os

template_path = r'd:\erp_thirteen\tp_education_system\backend\templates\枣阳市机关事业单位养老保险改革过渡期内职务升降退休人员信息申报表htm.htm'

print("=== 检查模板中的花括号内容 ===\n")

if os.path.exists(template_path):
    # 尝试多种编码
    encodings = ['utf-8', 'gbk', 'gb2312', 'gb18030', 'latin-1']
    content = None
    used_encoding = None
    
    for encoding in encodings:
        try:
            with open(template_path, 'r', encoding=encoding) as f:
                content = f.read()
                used_encoding = encoding
                break
        except:
            continue
    
    if content:
        print(f"使用编码: {used_encoding}")
        print(f"文件大小: {len(content)} 字符\n")
        
        # 查找所有花括号内容
        matches = re.findall(r'\{([^}]+)\}', content)
        print(f"找到 {len(matches)} 个花括号匹配:\n")
        
        for i, m in enumerate(matches, 1):
            print(f"{i}. '{m}'")
    else:
        print("无法读取文件")
else:
    print(f"文件不存在: {template_path}")
