#!/usr/bin/env python3
"""检查PDF中的文本内容"""
import pdfplumber

pdf_path = r'd:\erp_thirteen\tp_education_system\backend\templates\职工退休申报表.pdf'

with pdfplumber.open(pdf_path) as pdf:
    print(f"总页数: {len(pdf.pages)}")
    
    # 检查第1页
    page = pdf.pages[0]
    print(f"\n第1页尺寸: {page.width} x {page.height}")
    
    # 提取所有文本
    text = page.extract_text()
    print(f"\n第1页文本内容:\n{text[:1000]}")
    
    # 提取词语
    words = page.extract_words()
    print(f"\n\n第1页词语数量: {len(words)}")
    
    # 查找包含"同意"和"同志"的词
    print("\n包含'同意'的词:")
    for w in words:
        if '同意' in w['text']:
            print(f"  {w['text']} at ({w['x0']:.1f}, {w['top']:.1f})")
    
    print("\n包含'同志'的词:")
    for w in words:
        if '同志' in w['text']:
            print(f"  {w['text']} at ({w['x0']:.1f}, {w['top']:.1f})")
    
    print("\n包含'姓名'的词:")
    for w in words:
        if '姓名' in w['text']:
            print(f"  {w['text']} at ({w['x0']:.1f}, {w['top']:.1f})")
    
    # 显示前50个词
    print("\n\n前50个词:")
    for i, w in enumerate(words[:50]):
        print(f"{i}: {w['text']} at ({w['x0']:.1f}, {w['top']:.1f})")
