#!/usr/bin/env python3
"""测试坐标转换"""
import pdfplumber
from pdf2image import convert_from_path

pdf_path = "d:\\erp_thirteen\\tp_education_system\\backend\\templates\\职工退休申报表.pdf"
POPPLER_PATH = r'd:\erp_thirteen\tools\poppler-24.08.0\Library\bin'

# 获取PDF尺寸
with pdfplumber.open(pdf_path) as pdf:
    pdf_page = pdf.pages[1]  # 第2页
    pdf_width = pdf_page.width
    pdf_height = pdf_page.height
    print(f"PDF尺寸: {pdf_width} x {pdf_height}")

# 获取图片尺寸
images = convert_from_path(pdf_path, dpi=150, first_page=2, last_page=2, poppler_path=POPPLER_PATH)
img = images[0]
img_width, img_height = img.size
print(f"图片尺寸: {img_width} x {img_height}")

# 计算缩放比例
scale = img_width / pdf_width
print(f"\n缩放比例: {scale:.4f}")

# 测试坐标转换
test_points = [
    ("姓名值单元格", 177.7, 89.9),
    ("性别值单元格", 335.0, 89.9),
    ("出生年月值单元格", 500.8, 89.9),
]

print("\n坐标转换测试:")
for name, pdf_x, pdf_y in test_points:
    img_x = pdf_x * scale
    img_y = img_height - (pdf_y * scale)
    print(f"{name}:")
    print(f"  PDF: ({pdf_x}, {pdf_y})")
    print(f"  图片: ({img_x:.1f}, {img_y:.1f})")
