#!/usr/bin/env python3
"""调试表格结构"""
import pdfplumber

pdf_path = "d:\\erp_thirteen\\tp_education_system\\backend\\templates\\职工退休申报表.pdf"

with pdfplumber.open(pdf_path) as pdf:
    for page_num, page in enumerate(pdf.pages, 1):
        print(f"\n{'='*80}")
        print(f"第 {page_num} 页")
        print(f"{'='*80}")
        print(f"页面尺寸: {page.width} x {page.height}")
        
        tables = page.find_tables()
        print(f"\n检测到 {len(tables)} 个表格")
        
        for i, table in enumerate(tables):
            print(f"\n  表格 {i+1}:")
            print(f"    边界框: {table.bbox}")
            
            rows = table.rows
            print(f"    行数: {len(rows)}")
            
            for row_idx, row in enumerate(rows[:5]):  # 只显示前5行
                cells = row.cells
                print(f"\n    行 {row_idx+1} ({len(cells)} 个单元格):")
                for cell_idx, cell in enumerate(cells):
                    if cell:
                        x0, y0, x1, y1 = cell
                        print(f"      单元格 {cell_idx+1}: ({x0:.1f}, {y0:.1f}) - ({x1:.1f}, {y1:.1f})")
        
        # 如果没有检测到表格，显示所有文字
        if not tables:
            print("\n  未检测到表格，显示所有文字:")
            words = page.extract_words()
            for word in words[:30]:
                print(f"    '{word['text']}' - ({word['x0']:.1f}, {word['top']:.1f})")
