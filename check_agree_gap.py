#!/usr/bin/env python3
"""检查同意和同志之间的空白"""
import pdfplumber

pdf_path = r'd:\erp_thirteen\tp_education_system\backend\templates\职工退休申报表.pdf'

with pdfplumber.open(pdf_path) as pdf:
    page = pdf.pages[0]
    words = page.extract_words()
    
    print("查找'同意'和'同志'之间的空白:\n")
    
    # 找到所有同意和同志的位置
    agrees = [(i, w) for i, w in enumerate(words) if '同意' in w['text']]
    comrades = [(i, w) for i, w in enumerate(words) if '同志' in w['text']]
    
    for agree_idx, agree_word in agrees:
        print(f"\n同意: '{agree_word['text']}'")
        print(f"  位置: ({agree_word['x0']:.1f}, {agree_word['top']:.1f}) - ({agree_word['x1']:.1f}, {agree_word['bottom']:.1f})")
        
        # 查找同一行的同志
        for comrade_idx, comrade_word in comrades:
            y_diff = abs(comrade_word['top'] - agree_word['top'])
            if y_diff < 10:  # 同一行
                print(f"\n  同志: '{comrade_word['text']}'")
                print(f"    位置: ({comrade_word['x0']:.1f}, {comrade_word['top']:.1f}) - ({comrade_word['x1']:.1f}, {comrade_word['bottom']:.1f})")
                
                # 计算空白区域
                gap_start = agree_word['x1']
                gap_end = comrade_word['x0']
                gap_width = gap_end - gap_start
                
                print(f"\n  空白区域:")
                print(f"    起点: {gap_start:.1f}")
                print(f"    终点: {gap_end:.1f}")
                print(f"    宽度: {gap_width:.1f} pt")
                
                # 查找这个空白区域内的所有词
                words_in_gap = []
                for w in words:
                    if w['x0'] >= gap_start - 5 and w['x1'] <= gap_end + 5:
                        if abs(w['top'] - agree_word['top']) < 10:
                            words_in_gap.append(w)
                
                if words_in_gap:
                    print(f"\n  空白区域内的词:")
                    for w in sorted(words_in_gap, key=lambda x: x['x0']):
                        print(f"    '{w['text']}' at ({w['x0']:.1f}, {w['top']:.1f})")
                else:
                    print(f"\n  *** 这是一个空白填写区域 ***")
