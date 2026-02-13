#!/usr/bin/env python3
"""
调试字段提取算法 - 查看详细坐标信息
"""
import sys
sys.path.insert(0, 'd:\\erp_thirteen\\tp_education_system\\backend')

import pdfplumber
from services.field_extractor import PDFFieldExtractor, InputArea

def debug_extraction(pdf_path: str):
    """调试字段提取"""
    print(f"\n{'='*80}")
    print(f"调试文件: {pdf_path}")
    print(f"{'='*80}\n")
    
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages[:1], 1):  # 只处理第一页
            print(f"\n--- 第 {page_num} 页 ---")
            print(f"页面尺寸: {page.width} x {page.height}")
            
            # 获取所有文字
            words = page.extract_words()
            print(f"\n文字数量: {len(words)}")
            
            # 显示前20个文字的位置
            print("\n前20个文字:")
            for i, word in enumerate(words[:20]):
                print(f"  {i+1}. '{word['text']}' - x:{word['x0']:.1f}-{word['x1']:.1f}, y:{word['top']:.1f}-{word['bottom']:.1f}")
            
            # 查找表格
            tables = page.find_tables()
            print(f"\n表格数量: {len(tables)}")
            
            for i, table in enumerate(tables):
                print(f"\n  表格 {i+1}:")
                print(f"    边界: {table.bbox}")
                rows = table.rows
                print(f"    行数: {len(rows)}")
                
                # 显示第一行的单元格
                if rows:
                    first_row = rows[0]
                    cells = first_row.cells
                    print(f"    第一行单元格数: {len(cells)}")
                    for j, cell in enumerate(cells[:5]):  # 只显示前5个
                        if cell:
                            x0, y0, x1, y1 = cell
                            print(f"      单元格 {j+1}: x:{x0:.1f}-{x1:.1f}, y:{y0:.1f}-{y1:.1f}")
            
            # 测试提取
            print("\n" + "="*80)
            print("开始字段提取...")
            print("="*80)
            
            extractor = PDFFieldExtractor(pdf_path)
            extractor.pdf = pdf
            
            # 检测输入框区域
            input_areas = extractor._detect_input_areas(page, words)
            print(f"\n检测到 {len(input_areas)} 个输入框区域:")
            for i, area in enumerate(input_areas[:10]):  # 只显示前10个
                print(f"  {i+1}. 类型:{area.area_type} - x:{area.x0:.1f}-{area.x1:.1f}, y:{area.y0:.1f}-{area.y1:.1f}")
            
            # 检测标签
            labels = extractor._detect_labels(words)
            print(f"\n检测到 {len(labels)} 个标签:")
            for i, label in enumerate(labels[:10]):  # 只显示前10个
                print(f"  {i+1}. '{label['text']}' - x:{label['x0']:.1f}-{label['x1']:.1f}, y:{label['top']:.1f}-{label['bottom']:.1f}")
            
            # 为每个标签查找匹配的输入框
            print("\n标签-输入框配对结果:")
            for i, label in enumerate(labels[:5]):  # 只显示前5个
                area = extractor._find_matching_input_area(label, input_areas, words)
                if area:
                    center_x = (area.x0 + area.x1) / 2
                    center_y = (area.y0 + area.y1) / 2
                    print(f"\n  标签 '{label['text']}':")
                    print(f"    标签位置: x:{label['x0']:.1f}-{label['x1']:.1f}, y:{label['top']:.1f}-{label['bottom']:.1f}")
                    print(f"    输入框位置: x:{area.x0:.1f}-{area.x1:.1f}, y:{area.y0:.1f}-{area.y1:.1f}")
                    print(f"    标记点: ({center_x:.1f}, {center_y:.1f})")
                else:
                    print(f"\n  标签 '{label['text']}': 未找到匹配的输入框")

if __name__ == "__main__":
    pdf_path = "d:\\erp_thirteen\\tp_education_system\\backend\\templates\\职工退休申报表.pdf"
    debug_extraction(pdf_path)
