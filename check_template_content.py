#!/usr/bin/env python3
"""
检查模板文件内容
"""
import os

template_path = r'd:\erp_thirteen\tp_education_system\backend\templates\枣阳市机关事业单位养老保险改革过渡期内职务升降退休人员信息申报表htm.htm'

print("=== 检查模板文件内容 ===\n")

if os.path.exists(template_path):
    # 尝试多种编码
    encodings = ['utf-8', 'gbk', 'gb2312', 'gb18030']
    content = None
    used_encoding = None
    
    for encoding in encodings:
        try:
            with open(template_path, 'r', encoding=encoding) as f:
                content = f.read()
                used_encoding = encoding
                break
        except UnicodeDecodeError:
            continue
    
    if content:
        print(f"成功使用 {used_encoding} 编码读取文件")
        print(f"文件大小: {len(content)} 字符")
        print(f"\n前2000个字符:")
        print(content[:2000])
        
        # 查找可能的占位符模式
        import re
        print("\n\n查找所有花括号内容:")
        matches = re.findall(r'\{([^}]+)\}', content)
        for m in matches[:20]:
            print(f"  - {m}")
    else:
        print("无法读取文件")
else:
    print(f"文件不存在: {template_path}")
