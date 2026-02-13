#!/usr/bin/env python3
"""检查PDF第2页内容"""
import pdfplumber

pdf_path = r'd:\erp_thirteen\tp_education_system\backend\templates\职工退休申报表.pdf'

with pdfplumber.open(pdf_path) as pdf:
    print(f"总页数: {len(pdf.pages)}")
    
    if len(pdf.pages) >= 2:
        # 分析第2页
        page = pdf.pages[1]
        print(f"\n第2页尺寸: {page.width} x {page.height}")
        
        # 提取所有文本
        text = page.extract_text()
        print(f"\n第2页文本内容:\n{text}")
        
        # 提取词语及位置
        words = page.extract_words()
        print(f"\n\n第2页词语数量: {len(words)}")
        
        # 按Y坐标分组
        lines = {}
        for word in words:
            y_key = round(word['top'] / 10)
            if y_key not in lines:
                lines[y_key] = []
            lines[y_key].append(word)
        
        print("\n第2页布局:")
        for y_key in sorted(lines.keys()):
            line_words = sorted(lines[y_key], key=lambda x: x['x0'])
            line_text = ''.join([w['text'] for w in line_words])
            if line_text.strip():
                x_start = min(w['x0'] for w in line_words)
                x_end = max(w['x1'] for w in line_words)
                print(f"Y={y_key*10:3.0f}pt | X={x_start:6.1f}-{x_end:6.1f} | {line_text[:60]}")
    else:
        print("PDF只有1页")
