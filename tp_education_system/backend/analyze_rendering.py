import json

metadata_path = r'd:\erp_thirteen\tp_education_system\backend\data\templates\义务教育学校教职工绩效工资审批表_20260505_221848_20260505_222644.xlsx.metadata.json'

with open(metadata_path, 'r', encoding='utf-8') as f:
    metadata = json.load(f)

print("=" * 100)
print("检查元数据中第14行和第15行的所有单元格")
print("=" * 100)

for cell in metadata['cells']:
    if cell['row'] == 13 or cell['row'] == 14:  # row从0开始，所以14行是index 13
        print(f"\n单元格({cell['row']+1},{cell['col']+1}):")
        print(f"  value: '{cell['value']}'")
        print(f"  is_merged: {cell['is_merged']}")
        print(f"  is_master: {cell['is_master']}")
        print(f"  rowspan: {cell['rowspan']}")
        print(f"  colspan: {cell['colspan']}")
        print(f"  border: {cell['border']}")
        print(f"  font: {cell['font']}")
        print(f"  alignment: {cell['alignment']}")

print("\n" + "=" * 100)
print("检查合并单元格信息")
print("=" * 100)

for merge in metadata['merge_info']:
    if merge['row'] == 13 or merge['row'] == 14:
        print(f"\n合并单元格:")
        print(f"  起始位置: ({merge['row']+1},{merge['col']+1})")
        print(f"  类型: {merge['type']}")
        print(f"  rowspan: {merge['rowspan']}")
        print(f"  colspan: {merge['colspan']}")

print("\n" + "=" * 100)
print("模拟前端渲染逻辑")
print("=" * 100)

cellMap = {}
for cell in metadata['cells']:
    cellMap[f"{cell['row']}-{cell['col']}"] = cell

occupiedCells = set()

for row in range(metadata['sheet_info']['total_rows']):
    for col in range(metadata['sheet_info']['total_cols']):
        key = f"{row}-{col}"
        
        if key in occupiedCells:
            if row == 13 or row == 14:
                print(f"  单元格({row+1},{col+1}) 被跳过（已被占用）")
            continue
        
        cell = cellMap.get(key)
        
        if row == 13 or row == 14:
            if cell:
                print(f"  单元格({row+1},{col+1}) 渲染: '{cell['value']}'")
            else:
                print(f"  单元格({row+1},{col+1}) 渲染: (空)")
        
        if not cell:
            continue
        
        rowspan = cell.get('rowspan', 1)
        colspan = cell.get('colspan', 1)
        
        for r in range(rowspan):
            for c in range(colspan):
                occupiedCells.add(f"{row + r}-{col + c}")

print("=" * 100)
