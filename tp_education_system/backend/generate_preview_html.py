"""
生成HTML预览文件，模拟前端渲染结果
"""
import json

# 读取元数据
metadata_file = r"d:\erp_thirteen\tp_education_system\backend\data\templates\义务教育学校教职工绩效工资审批表_20260505_154157.xlsx.metadata.json"
with open(metadata_file, 'r', encoding='utf-8') as f:
    metadata = json.load(f)

# 创建单元格映射
cell_map = {}
for cell in metadata['cells']:
    cell_map[f"{cell['row']}-{cell['col']}"] = cell

# 模拟前端渲染逻辑
def build_cell_style(cell):
    styles = []
    
    styles.append('padding: 4px 6px')
    styles.append('vertical-align: middle')
    styles.append('white-space: pre-wrap')
    
    border = cell.get('border', {})
    has_border = border.get('top') or border.get('bottom') or border.get('left') or border.get('right')
    
    if has_border:
        if border.get('top'):
            styles.append(f"border-top: 1px solid {border['top'].get('color', '#000')}")
        else:
            styles.append('border-top: none')
        if border.get('bottom'):
            styles.append(f"border-bottom: 1px solid {border['bottom'].get('color', '#000')}")
        else:
            styles.append('border-bottom: none')
        if border.get('left'):
            styles.append(f"border-left: 1px solid {border['left'].get('color', '#000')}")
        else:
            styles.append('border-left: none')
        if border.get('right'):
            styles.append(f"border-right: 1px solid {border['right'].get('color', '#000')}")
        else:
            styles.append('border-right: none')
    else:
        styles.append('border: none')
    
    font = cell.get('font', {})
    if font.get('name'):
        styles.append(f"font-family: '{font['name']}', SimSun, serif")
    if font.get('size'):
        styles.append(f"font-size: {font['size']}pt")
    if font.get('bold'):
        styles.append('font-weight: bold')
    if font.get('italic'):
        styles.append('font-style: italic')
    if font.get('color'):
        styles.append(f"color: {font['color']}")
    
    alignment = cell.get('alignment', {})
    h_align = alignment.get('horizontal', 'center')
    
    if h_align == 'left' or h_align == 'general':
        styles.append('text-align: left')
    elif h_align == 'right':
        styles.append('text-align: right')
    else:
        styles.append('text-align: center')
    
    fill = cell.get('fill')
    if fill and fill.get('color'):
        styles.append(f"background-color: {fill['color']}")
    
    return '; '.join(styles)

# 生成HTML
total_rows = metadata['sheet_info']['total_rows']
total_cols = metadata['sheet_info']['total_cols']
row_heights = metadata.get('dimensions', {}).get('row_heights', {})
col_widths = metadata.get('dimensions', {}).get('col_widths', {})

html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>模板预览 - 模拟前端渲染</title>
    <style>
        body {
            font-family: SimSun, 宋体, serif;
            background: #f5f5f5;
            padding: 20px;
        }
        .paper-wrapper {
            background: #e0e0e0;
            width: 210mm;
            height: 297mm;
            margin: 0 auto;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
        }
        .content-wrapper {
            background: white;
            padding: 15mm;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
            transform: scale(0.76);
            transform-origin: top left;
            width: 276.32mm;
            min-height: 390.79mm;
        }
        table {
            border-collapse: collapse;
            width: 100%;
            table-layout: fixed;
        }
        td {
            padding: 4px 6px;
        }
    </style>
</head>
<body>
    <h1>模板预览 - 模拟前端渲染结果</h1>
    <p>如果此页面与原Excel不一致，请查看源代码找出问题</p>
    <hr>
    <div class="paper-wrapper">
        <div class="content-wrapper">
            <table>
                <colgroup>
"""

# 添加列宽
for col in range(total_cols):
    width = col_widths.get(str(col), 80)
    html += f'                    <col style="width: {width}px;">\n'

html += """                </colgroup>
"""

# 添加单元格
occupied_cells = set()

for row in range(total_rows):
    height = row_heights.get(str(row), 25)
    html += f'                <tr style="height: {height}pt;">\n'
    
    for col in range(total_cols):
        key = f"{row}-{col}"
        
        if key in occupied_cells:
            continue
        
        cell = cell_map.get(key)
        
        if not cell:
            html += '                    <td style="border: 1px solid #000; padding: 4px;">&nbsp;</td>\n'
            continue
        
        rowspan = cell.get('rowspan', 1)
        colspan = cell.get('colspan', 1)
        
        # 标记占用的单元格
        for r in range(rowspan):
            for c in range(colspan):
                occupied_cells.add(f"{row + r}-{col + c}")
        
        style = build_cell_style(cell)
        value = cell.get('value', '') or '&nbsp;'
        
        rowspan_attr = f' rowspan="{rowspan}"' if rowspan > 1 else ''
        colspan_attr = f' colspan="{colspan}"' if colspan > 1 else ''
        
        html += f'                    <td{rowspan_attr}{colspan_attr} style="{style}">{value}</td>\n'
    
    html += '                </tr>\n'

html += """            </table>
        </div>
    </div>
</body>
</html>
"""

# 保存HTML文件
output_file = r"d:\erp_thirteen\tp_education_system\backend\preview_simulation.html"
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"HTML文件已生成: {output_file}")
print("请用浏览器打开此文件，与原Excel对比")
