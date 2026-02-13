#!/usr/bin/env python3
"""分析PDF结构，用于设计网页版表单"""
import pdfplumber

pdf_path = r'd:\erp_thirteen\tp_education_system\backend\templates\职工退休申报表.pdf'

with pdfplumber.open(pdf_path) as pdf:
    print(f"总页数: {len(pdf.pages)}")
    print(f"页面尺寸: {pdf.pages[0].width} x {pdf.pages[0].height}")
    
    # 分析第1页布局
    page = pdf.pages[0]
    
    # 提取所有文本及其位置
    words = page.extract_words()
    
    print("\n=== 第1页文本布局分析 ===\n")
    
    # 按Y坐标分组（行）
    lines = {}
    for word in words:
        y_key = round(word['top'] / 10)  # 每10pt为一行
        if y_key not in lines:
            lines[y_key] = []
        lines[y_key].append(word)
    
    # 按行输出
    for y_key in sorted(lines.keys()):
        line_words = sorted(lines[y_key], key=lambda x: x['x0'])
        line_text = ''.join([w['text'] for w in line_words])
        if line_text.strip():
            x_start = min(w['x0'] for w in line_words)
            x_end = max(w['x1'] for w in line_words)
            print(f"Y={y_key*10:3.0f}pt | X={x_start:6.1f}-{x_end:6.1f} | {line_text[:60]}")
