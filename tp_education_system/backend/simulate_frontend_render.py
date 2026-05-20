"""
模拟前端渲染逻辑，找出问题
"""
import json

# 读取元数据
metadata_file = r"d:\erp_thirteen\tp_education_system\backend\data\templates\义务教育学校教职工绩效工资审批表_20260505_154157.xlsx.metadata.json"
with open(metadata_file, 'r', encoding='utf-8') as f:
    metadata = json.load(f)

# 创建单元格映射
cellMap = {}
for cell in metadata['cells']:
    cellMap[f"{cell['row']}-{cell['col']}"] = cell

# 模拟前端渲染逻辑
totalRows = 31
totalCols = 6
occupiedCells = set()

print("=" * 120)
print("模拟前端渲染逻辑")
print("=" * 120)

# 第一遍：标记所有被合并单元格占用的单元格
print("\n标记合并单元格占用的单元格：")
for key, cell in cellMap.items():
    row = cell['row']
    col = cell['col']
    rowspan = cell.get('rowspan', 1)
    colspan = cell.get('colspan', 1)
    
    if rowspan > 1 or colspan > 1:
        print(f"  单元格({row+1}, {col+1}): {rowspan}行×{colspan}列")
        for r in range(rowspan):
            for c in range(colspan):
                occupiedKey = f"{row + r}-{col + c}"
                occupiedCells.add(occupiedKey)
                print(f"    标记: {occupiedKey}")

print(f"\n总共标记了 {len(occupiedCells)} 个单元格")

# 第二遍：检查哪些单元格会被渲染
print("\n" + "=" * 120)
print("检查渲染结果")
print("=" * 120)

rendered = 0
skipped = 0
empty = 0

for row in range(totalRows):
    for col in range(totalCols):
        key = f"{row}-{col}"
        
        if key in occupiedCells:
            skipped += 1
            continue
        
        cell = cellMap.get(key)
        
        if not cell:
            empty += 1
            print(f"  单元格({row+1}, {col+1}): 不在cellMap中，会渲染空单元格")
        else:
            rendered += 1

print(f"\n统计：")
print(f"  渲染的单元格: {rendered}")
print(f"  跳过的单元格（被合并）: {skipped}")
print(f"  空单元格（不在cellMap中）: {empty}")
print(f"  总计: {rendered + skipped + empty}")

print("\n问题：")
print("  空单元格应该为0，因为所有不在cellMap中的单元格都应该被occupiedCells标记")
print(f"  但实际有 {empty} 个空单元格")
print("  这说明前端渲染逻辑有问题")
