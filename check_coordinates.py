#!/usr/bin/env python3
"""检查PDF坐标系统"""
import pdfplumber

pdf_path = "d:\\erp_thirteen\\tp_education_system\\backend\\templates\\职工退休申报表.pdf"

with pdfplumber.open(pdf_path) as pdf:
    page = pdf.pages[1]  # 第2页
    
    print(f"页面尺寸: {page.width} x {page.height}")
    print(f"cropbox: {page.cropbox}")
    print(f"mediabox: {page.mediabox}")
    
    # 获取所有文字
    words = page.extract_words()
    
    # 按Y坐标排序
    words_by_y = sorted(words, key=lambda w: w['top'])
    
    print("\n最上方的文字（Y坐标最小）:")
    for word in words_by_y[:5]:
        print(f"  '{word['text']}' - Y: {word['top']:.1f}")
    
    print("\n最下方的文字（Y坐标最大）:")
    for word in words_by_y[-5:]:
        print(f"  '{word['text']}' - Y: {word['top']:.1f}")
    
    # 查找"姓名"
    print("\n'姓名'的位置:")
    for word in words:
        if word['text'] == '姓名':
            print(f"  x: {word['x0']:.1f}-{word['x1']:.1f}, y: {word['top']:.1f}-{word['bottom']:.1f}")
