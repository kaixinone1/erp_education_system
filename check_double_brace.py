#!/usr/bin/env python3
"""
检查双花括号占位符
"""
import re
import os

template_path = r'd:\erp_thirteen\tp_education_system\backend\templates\枣阳市机关事业单位养老保险改革过渡期内职务升降退休人员信息申报表htm.htm'

print("=== 检查双花括号占位符 ===\n")

if os.path.exists(template_path):
    # 读取文件
    encodings = ['utf-8', 'gbk', 'gb2312', 'gb18030']
    content = None
    for encoding in encodings:
        try:
            with open(template_path, 'r', encoding=encoding) as f:
                content = f.read()
                print(f"使用 {encoding} 编码读取成功")
                break
        except:
            continue
    
    if content:
        # 查找 {{...}}
        matches = re.findall(r'\{\{([^}]+)\}\}', content)
        print(f"\n找到 {len(matches)} 个双花括号内容:\n")
        for i, m in enumerate(matches[:20], 1):
            print(f"{i}. {repr(m)}")
        
        # 也查找附近的内容
        print("\n\n查找包含 {{ 的行:")
        for line in content.split('\n'):
            if '{{' in line:
                print(f"  {line[:200]}")
    else:
        print("无法读取文件")
else:
    print("文件不存在")
