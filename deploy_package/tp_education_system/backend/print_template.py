import json
d = json.load(open('data/template_meta.json', 'r', encoding='utf-8'))

ps = d.get('page_setup', {})
print('=' * 60)
print('1. 页面设置')
print('=' * 60)
print(f'纸张尺寸: A4竖放 ({ps.get("paper_width")}pt x {ps.get("paper_height")}pt)')
print(f'页边距: 上{ps.get("margins", {}).get("top")}pt 下{ps.get("margins", {}).get("bottom")}pt 左{ps.get("margins", {}).get("left")}pt 右{ps.get("margins", {}).get("right")}pt')
print(f'表格总宽度: {ps.get("table_width")}pt')
print(f'总行数: {d.get("total_rows", 0)}')

print('\n' + '=' * 60)
print('2. 各行详细内容')
print('=' * 60)

for r in range(min(35, len(d['rows']))):
    row = d['rows'][r]
    print(f'\n--- 行{r} (高度: {row["height"]}pt) ---')
    print(f'单元格数: {len(row["cells"])}')
    
    # 只打印有内容的单元格
    for i, cell in enumerate(row['cells']):
        if cell['text']:
            rs = cell['rowspan']
            cs = cell['colspan']
            merge = ''
            if rs > 1 or cs > 1:
                merge = f' [合并: r{rs}c{cs}]'
            print(f'  单元格{i}: {cell["text"]}{merge}')
