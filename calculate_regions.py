#!/usr/bin/env python3
"""计算A3四区域坐标"""

# PDF实际尺寸
PAGE_WIDTH = 1190.55  # pt
PAGE_HEIGHT = 841.85  # pt

# 页边距 3cm = 85pt
MARGIN = 85

# 计算有效区域
effective_width = PAGE_WIDTH - 2 * MARGIN  # 1020.55 pt
effective_height = PAGE_HEIGHT - 2 * MARGIN  # 671.85 pt

# 中线位置（左右栏分隔）
mid_x = PAGE_WIDTH / 2  # 595.275 pt

print("=" * 50)
print("A3纸四区域计算")
print("=" * 50)
print(f"\n页面尺寸: {PAGE_WIDTH} × {PAGE_HEIGHT} pt")
print(f"页边距: {MARGIN} pt (3cm)")
print(f"有效区域宽度: {effective_width} pt")
print(f"有效区域高度: {effective_height} pt")
print(f"中线X坐标: {mid_x} pt")

print("\n" + "=" * 50)
print("第1页（正面）- 区域1和区域2")
print("=" * 50)

# 第1页 - 区域1（左栏）
print("\n区域1（左栏-正面）:")
print(f"  左边界 x0: {MARGIN} pt")
print(f"  上边界 y0: {MARGIN} pt")
print(f"  右边界 x1: {mid_x} pt")
print(f"  下边界 y1: {PAGE_HEIGHT - MARGIN} pt")
print(f"  宽度: {mid_x - MARGIN} pt ({(mid_x - MARGIN) * 0.3528:.1f} mm)")

# 第1页 - 区域2（右栏）
print("\n区域2（右栏-正面）:")
print(f"  左边界 x0: {mid_x} pt")
print(f"  上边界 y0: {MARGIN} pt")
print(f"  右边界 x1: {PAGE_WIDTH - MARGIN} pt")
print(f"  下边界 y1: {PAGE_HEIGHT - MARGIN} pt")
print(f"  宽度: {PAGE_WIDTH - MARGIN - mid_x} pt ({(PAGE_WIDTH - MARGIN - mid_x) * 0.3528:.1f} mm)")

print("\n" + "=" * 50)
print("第2页（背面）- 区域3和区域4")
print("=" * 50)

# 第2页 - 区域3（左栏）
print("\n区域3（左栏-背面）:")
print(f"  左边界 x0: {MARGIN} pt")
print(f"  上边界 y0: {MARGIN} pt")
print(f"  右边界 x1: {mid_x} pt")
print(f"  下边界 y1: {PAGE_HEIGHT - MARGIN} pt")

# 第2页 - 区域4（右栏）
print("\n区域4（右栏-背面）:")
print(f"  左边界 x0: {mid_x} pt")
print(f"  上边界 y0: {MARGIN} pt")
print(f"  右边界 x1: {PAGE_WIDTH - MARGIN} pt")
print(f"  下边界 y1: {PAGE_HEIGHT - MARGIN} pt")

print("\n" + "=" * 50)
print("栏宽验证")
print("=" * 50)
栏宽_pt = mid_x - MARGIN
print(f"每栏宽度: {栏宽_pt} pt")
print(f"每栏宽度: {栏宽_pt * 0.3528:.1f} mm")
# 假设字符宽度约10.5pt (小四号字)
字符数 = 栏宽_pt / 10.5
print(f"按10.5pt/字符计算: 约 {字符数:.1f} 字符")
