#!/usr/bin/env python3
"""调试姓名字段位置"""
import pdfplumber

pdf_path = "d:\\erp_thirteen\\tp_education_system\\backend\\templates\\职工退休申报表.pdf"

with pdfplumber.open(pdf_path) as pdf:
    page = pdf.pages[1]  # 第2页
    
    print("第2页分析")
    print("="*80)
    
    # 获取所有文字
    words = page.extract_words()
    
    # 查找"姓名"
    for word in words:
        if '姓名' in word['text']:
            print(f"\n找到'姓名': {word}")
    
    # 查找表格
    tables = page.find_tables()
    print(f"\n表格数量: {len(tables)}")
    
    # 检查每个表格
    for i, table in enumerate(tables):
        print(f"\n表格 {i+1} 边界: {table.bbox}")
        rows = table.rows
        
        for row_idx, row in enumerate(rows[:3]):  # 只看前3行
            cells = row.cells
            print(f"\n  行 {row_idx+1}:")
            
            for cell_idx, cell in enumerate(cells):
                if not cell:
                    continue
                    
                x0, y0, x1, y1 = cell
                
                # 检查这个单元格是否包含"姓名"
                cell_words = []
                for word in words:
                    word_x = (word['x0'] + word['x1']) / 2
                    word_y = (word['top'] + word['bottom']) / 2
                    if x0 <= word_x <= x1 and y0 <= word_y <= y1:
                        cell_words.append(word['text'])
                
                cell_text = ''.join(cell_words)
                
                center_x = (x0 + x1) / 2
                center_y = (y0 + y1) / 2
                
                print(f"    单元格 {cell_idx+1}: ({x0:.1f}, {y0:.1f}) - ({x1:.1f}, {y1:.1f})")
                print(f"      内容: '{cell_text}'")
                print(f"      中心: ({center_x:.1f}, {center_y:.1f})")
