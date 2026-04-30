from bs4 import BeautifulSoup
import json
import os
import re

def parse_template():
    template_file = os.path.join(
        os.path.dirname(__file__), 
        'templates', 
        '义务教育学校教职工绩效工资审批表(1).html'
    )
    
    with open(template_file, 'r', encoding='utf-8') as f:
        html = f.read()
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # 提取页面设置
    page_setup = {
        'margins': {'top': 72, 'bottom': 72, 'left': 54, 'right': 54},
        'paper_width': 595,
        'paper_height': 842,
        'orientation': 'portrait'
    }
    
    # 从HTML中提取页边距
    margin_match = re.search(r'margin:([^;]+)', html)
    if margin_match:
        margins = margin_match.group(1).split()
        if len(margins) == 4:
            page_setup['margins'] = {
                'top': int(float(margins[0].replace('in','')) * 72),
                'right': int(float(margins[1].replace('in','')) * 72),
                'bottom': int(float(margins[2].replace('in','')) * 72),
                'left': int(float(margins[3].replace('in','')) * 72)
            }
    
    # 提取表格宽度
    table = soup.find('table')
    table_width = table.get('width', '')
    if table_width:
        width_match = re.match(r'(\d+\.?\d*)', table_width)
        if width_match:
            page_setup['table_width'] = float(width_match.group(1))
    
    # 获取colgroup列宽
    colgroup = table.find('colgroup')
    col_widths = []
    if colgroup:
        for col in colgroup.find_all('col'):
            width = col.get('width', '100')
            col_widths.append(width)
    
    # 获取所有行
    rows = table.find_all('tr')
    table_data = []
    
    for row_idx, row in enumerate(rows):
        row_data = {
            'height': row.get('height', '25'),
            'cells': []
        }
        
        cells = row.find_all(['td', 'th'])
        
        for cell in cells:
            text = cell.get_text(strip=True)
            
            x_str = cell.get('x:str', '')
            if x_str and not text:
                text = x_str
            
            rowspan = cell.get('rowspan')
            colspan = cell.get('colspan')
            
            cell_data = {
                'text': text,
                'rowspan': int(rowspan) if rowspan else 1,
                'colspan': int(colspan) if colspan else 1,
                'height': cell.get('height', ''),
                'style': cell.get('style', ''),
                'class': cell.get('class', []),
                'width': cell.get('width', '')
            }
            row_data['cells'].append(cell_data)
        
        table_data.append(row_data)
    
    result = {
        'page_setup': page_setup,
        'col_widths': col_widths,
        'rows': table_data,
        'total_rows': len(rows)
    }
    
    return result

if __name__ == '__main__':
    result = parse_template()
    print('文件名: 义务教育学校教职工绩效工资审批表(1).html')
    print(f"总行数: {result['total_rows']}")
    print(f"页面设置: {result['page_setup']}")
    print(f"表格宽度: {result.get('table_width', 'N/A')}")
    print(f"列宽: {len(result['col_widths'])}")
    print(f"第一行: {len(result['rows'][0]['cells'])}个单元格")
    
    # 保存到文件
    output_file = os.path.join(
        os.path.dirname(__file__), 
        'data', 
        'template_meta.json'
    )
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"已保存到: {output_file}")
