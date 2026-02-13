#!/usr/bin/env python3
"""检查模板文件中"供养直系亲属"单元格的结构"""

from docx import Document

def check_template():
    template_path = r'd:\erp_thirteen\职工退休呈报表.docx'
    doc = Document(template_path)
    
    print("=== 查找包含'供养直系亲属'的单元格 ===")
    for table_idx, table in enumerate(doc.tables):
        for row_idx, row in enumerate(table.rows):
            for cell_idx, cell in enumerate(row.cells):
                text = cell.text.strip()
                if '供养直系亲属' in text:
                    print(f"\n表格 {table_idx}, 行 {row_idx}, 列 {cell_idx}")
                    print(f"单元格内容: {repr(text)}")
                    print(f"行中单元格数量: {len(row.cells)}")
                    # 检查下一个单元格
                    if cell_idx + 1 < len(row.cells):
                        next_cell_text = row.cells[cell_idx + 1].text.strip()
                        print(f"下一个单元格内容: {repr(next_cell_text)}")
                    else:
                        print("没有下一个单元格")

if __name__ == '__main__':
    check_template()
