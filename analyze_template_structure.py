#!/usr/bin/env python3
"""
分析模板文件结构，自动识别可填充区域
"""
import re
import os
from bs4 import BeautifulSoup

def analyze_html_template(file_path):
    """分析HTML模板结构"""
    # 尝试多种编码读取
    encodings = ['utf-8', 'gbk', 'gb2312', 'gb18030']
    content = None
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
                break
        except:
            continue
    
    if not content:
        return []
    
    # 使用BeautifulSoup解析
    soup = BeautifulSoup(content, 'html.parser')
    
    # 查找所有表格单元格
    fields = []
    
    # 方法1: 查找所有td和th中的文本
    for idx, cell in enumerate(soup.find_all(['td', 'th'])):
        text = cell.get_text(strip=True)
        # 如果单元格包含文本且不是纯标签名
        if text and len(text) < 50:
            # 检查是否是标签/标题（通常是较短的文本）
            # 或者是可填充区域（如"____"、空白等）
            if text in ['姓名', '性别', '出生日期', '民族', '文化程度', '身份证号码']:
                fields.append({
                    'type': 'label',
                    'text': text,
                    'index': idx
                })
    
    # 方法2: 查找input标签
    for idx, inp in enumerate(soup.find_all('input')):
        name = inp.get('name') or inp.get('id') or f'input_{idx}'
        fields.append({
            'type': 'input',
            'name': name,
            'index': idx
        })
    
    return fields

# 分析模板
template_path = r'd:\erp_thirteen\tp_education_system\backend\templates\枣阳市机关事业单位养老保险改革过渡期内职务升降退休人员信息申报表htm.htm'

print("=== 分析模板结构 ===\n")

if os.path.exists(template_path):
    fields = analyze_html_template(template_path)
    print(f"找到 {len(fields)} 个潜在字段区域")
    for f in fields[:20]:
        print(f"  - {f}")
else:
    print("模板文件不存在")
