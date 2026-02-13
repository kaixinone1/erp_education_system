#!/usr/bin/env python3
"""将PDF两页转换为PNG图片"""
import fitz
import os

pdf_path = r'd:\erp_thirteen\tp_education_system\backend\templates\职工退休申报表.pdf'
output_dir = r'd:\erp_thirteen\tp_education_system\frontend\public\templates'

os.makedirs(output_dir, exist_ok=True)

doc = fitz.open(pdf_path)

for page_num in range(len(doc)):
    page = doc[page_num]
    zoom = 2
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat)
    
    output_path = os.path.join(output_dir, f'职工退休申报表_page{page_num + 1}.png')
    pix.save(output_path)
    print(f"已保存第{page_num + 1}页: {output_path} ({pix.width}x{pix.height})")

doc.close()
print("转换完成")
