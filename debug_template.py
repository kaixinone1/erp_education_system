#!/usr/bin/env python3
"""
调试模板文件，查找所有{}内容
"""
import re
import os

template_path = r'd:\erp_thirteen\tp_education_system\backend\templates\枣阳市机关事业单位养老保险改革过渡期内职务升降退休人员信息申报表htm.htm'

print("=== 调试模板文件 ===\n")

if os.path.exists(template_path):
    # 读取文件内容
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
        # 查找所有{}中的内容
        matches = re.findall(r'\{([^}]+)\}', content)
        print(f"\n找到 {len(matches)} 个花括号内容:\n")
        
        for i, m in enumerate(matches[:50], 1):
            m = m.strip()
            # 显示原始内容和编码
            print(f"{i}. 原始: {repr(m)}")
            print(f"   显示: {m}")
            print()
    else:
        print("无法读取文件")
else:
    print("文件不存在")
