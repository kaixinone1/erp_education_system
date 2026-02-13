#!/usr/bin/env python3
"""计算44.6字符对应的区域宽度"""

# PDF实际尺寸
PAGE_WIDTH = 1190.55  # pt
PAGE_HEIGHT = 841.85  # pt

# 页边距 3cm = 85pt
MARGIN = 85

# 栏宽 44.6字符
CHARS_PER_COL = 44.6

# 估算字符宽度（根据44.6字符计算）
# 有效宽度 = 1190.55 - 85*2 = 1020.55 pt
# 如果中间有装订线，假设装订线宽度为 binding_space

# 方案1: 按字符宽度10pt计算（常用字号）
char_width_10pt = 10
栏宽_10pt = CHARS_PER_COL * char_width_10pt
print(f"按10pt/字符计算:")
print(f"  栏宽 = {CHARS_PER_COL} × {char_width_10pt} = {栏宽_10pt} pt")
print(f"  两栏总宽 = {栏宽_10pt * 2} pt")
print(f"  中间装订线 = {PAGE_WIDTH - 2*MARGIN - 栏宽_10pt*2} pt")

# 方案2: 按字符宽度11pt计算
char_width_11pt = 11
栏宽_11pt = CHARS_PER_COL * char_width_11pt
print(f"\n按11pt/字符计算:")
print(f"  栏宽 = {CHARS_PER_COL} × {char_width_11pt} = {栏宽_11pt} pt")
print(f"  两栏总宽 = {栏宽_11pt * 2} pt")
print(f"  中间装订线 = {PAGE_WIDTH - 2*MARGIN - 栏宽_11pt*2} pt")

# 方案3: 按实际页面空间计算（假设中间装订线约20pt）
binding_space = 20
available_width = PAGE_WIDTH - 2*MARGIN - binding_space  # 1000.55 pt
char_width_actual = available_width / 2 / CHARS_PER_COL
print(f"\n按实际空间计算（装订线{binding_space}pt）:")
print(f"  可用宽度 = {available_width} pt")
print(f"  每栏宽度 = {available_width/2} pt")
print(f"  字符宽度 = {char_width_actual:.2f} pt/字符")

# 推荐方案
print("\n" + "="*50)
print("推荐方案:")
print("="*50)
print(f"页边距: {MARGIN} pt (3cm)")
print(f"装订线: {binding_space} pt (约7mm)")
print(f"每栏宽度: {available_width/2:.1f} pt ({available_width/2*0.3528:.1f} mm)")
print(f"每栏字符数: {CHARS_PER_COL} 字符")

# 计算区域坐标
left_col_x0 = MARGIN
left_col_x1 = MARGIN + available_width/2
right_col_x0 = left_col_x1 + binding_space
right_col_x1 = right_col_x0 + available_width/2

print(f"\n区域坐标:")
print(f"  左栏: x0={left_col_x0}, x1={left_col_x1:.1f}")
print(f"  右栏: x0={right_col_x0:.1f}, x1={right_col_x1:.1f}")
