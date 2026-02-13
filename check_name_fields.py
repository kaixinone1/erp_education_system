#!/usr/bin/env python3
"""检查姓名字段位置"""
import pdfplumber

pdf_path = r'd:\erp_thirteen\tp_education_system\backend\templates\职工退休申报表.pdf'

with pdfplumber.open(pdf_path) as pdf:
    page = pdf.pages[0]
    words = page.extract_words()
    
    print("查找所有'同意'和'同志'的位置关系:\n")
    
    # 找到所有同意和同志的位置
    agrees = [(i, w) for i, w in enumerate(words) if '同意' in w['text']]
    comrades = [(i, w) for i, w in enumerate(words) if '同志' in w['text']]
    
    print(f"找到 {len(agrees)} 个'同意'和 {len(comrades)} 个'同志'\n")
    
    for agree_idx, agree_word in agrees:
        print(f"同意 #{agree_idx}: '{agree_word['text']}' at ({agree_word['x0']:.1f}, {agree_word['top']:.1f})")
        
        # 查找同一行或相近y坐标的同志
        for comrade_idx, comrade_word in comrades:
            y_diff = abs(comrade_word['top'] - agree_word['top'])
            if y_diff < 5:  # 同一行
                x_gap = comrade_word['x0'] - agree_word['x1']
                print(f"  -> 同志 #{comrade_idx}: '{comrade_word['text']}' at ({comrade_word['x0']:.1f}, {comrade_word['top']:.1f})")
                print(f"     X间距: {x_gap:.1f}pt")
                
                # 检查中间是否有空白
                if x_gap > 10:
                    print(f"     *** 找到姓名字段位置: x={agree_word['x1']:.1f}, width={x_gap:.1f}")
        print()
    
    print("\n查找'姓名：'位置:\n")
    for i, w in enumerate(words):
        if '姓名' in w['text']:
            print(f"姓名 #{i}: '{w['text']}' at ({w['x0']:.1f}, {w['top']:.1f})")
            # 查找冒号
            for j in range(i, min(i+3, len(words))):
                if '：' in words[j]['text'] or ':' in words[j]['text']:
                    colon_word = words[j]
                    print(f"  -> 冒号: '{colon_word['text']}' at ({colon_word['x0']:.1f}, {colon_word['top']:.1f})")
                    # 查找冒号后面的内容
                    if j + 1 < len(words):
                        next_word = words[j + 1]
                        gap = next_word['x0'] - colon_word['x1']
                        print(f"  -> 下一个词: '{next_word['text']}' at ({next_word['x0']:.1f}, {next_word['top']:.1f})")
                        print(f"     间距: {gap:.1f}pt")
                        if gap > 10:
                            print(f"     *** 找到姓名字段位置: x={colon_word['x1']:.1f}, width={gap:.1f}")
