#!/usr/bin/env python3
"""
检查模板中所有可能的占位符
"""
import os
import re

template_path = r'd:\erp_thirteen\tp_education_system\backend\templates\枣阳市机关事业单位养老保险改革过渡期内职务升降退休人员信息申报表htm.htm'

print("=== 检查模板中所有可能的占位符 ===\n")

if os.path.exists(template_path):
    # 读取文件
    with open(template_path, 'rb') as f:
        raw_content = f.read()
    
    # 尝试检测编码
    import chardet
    detected = chardet.detect(raw_content)
    encoding = detected['encoding']
    print(f"检测到的编码: {encoding}")
    
    # 解码内容
    try:
        content = raw_content.decode(encoding)
    except:
        content = raw_content.decode('gbk', errors='ignore')
    
    # 查找所有花括号内容
    print("\n查找所有 {xxx} 格式的内容:")
    matches = re.findall(r'\{([^}]+)\}', content)
    
    valid_matches = []
    for m in matches[:30]:
        m = m.strip()
        # 简单的有效性检查
        if len(m) < 50 and not any(kw in m.lower() for kw in ['mso-', 'style', 'font-', 'if gte', 'endif']):
            valid_matches.append(m)
            print(f"  - {m}")
    
    print(f"\n找到 {len(valid_matches)} 个可能的占位符")
    
    # 查找input标签
    print("\n查找所有input标签:")
    inputs = re.findall(r'<input[^>]*>', content, re.IGNORECASE)
    print(f"找到 {len(inputs)} 个input标签")
    
else:
