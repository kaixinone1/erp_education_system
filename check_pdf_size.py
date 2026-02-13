#!/usr/bin/env python3
"""检查PDF页面尺寸"""
import pdfplumber

pdf_path = r'd:\erp_thirteen\tp_education_system\backend\templates\职工退休申报表.pdf'

with pdfplumber.open(pdf_path) as pdf:
    print(f"总页数: {len(pdf.pages)}")
    for i, page in enumerate(pdf.pages, 1):
        print(f"\n第{i}页:")
        print(f"  宽度: {page.width} pt ({page.width * 0.3528:.2f} mm)")
        print(f"  高度: {page.height} pt ({page.height * 0.3528:.2f} mm)")
        print(f"  是否是A3: {'是' if page.width > 800 else '否'}")
