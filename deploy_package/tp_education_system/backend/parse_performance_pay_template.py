import os
import json
import re
from bs4 import BeautifulSoup

def parse_template():
    template_file = r"D:\erp_thirteen\数据库信息\模板\义务教育学校教职工绩效工资审批表(1).html"
    
    with open(template_file, 'r', encoding='utf-8') as f:
        html = f.read()
    
    soup = BeautifulSoup(html, 'html.parser')
    
    page_setup = {
        'margins': {'top': 72, 'bottom': 72, 'left': 54, 'right': 54},
        'paper_width': 595,
        'paper_height': 842,
        'orientation': 'portrait',
        'original_table_width': 807.75,
        'scale': 0.7366
    }
    
    margin_match = re.search(r'margin:([0-9.]+)in\s+([0-9.]+)in\s+([0-9.]+)in\s+([0-9.]+)in', html)
    if margin_match:
        page_setup['margins'] = {
            'top': int(float(margin_match.group(1)) * 72),
            'right': int(float(margin_match.group(2)) * 72),
            'bottom': int(float(margin_match.group(3)) * 72),
            'left': int(float(margin_match.group(4)) * 72)
        }
    
    table = soup.find('table')
    
    table_width_match = re.search(r'width:([0-9.]+)pt', table.get('style', ''))
    if table_width_match:
        original_width = float(table_width_match.group(1))
        page_setup['original_table_width'] = original_width
        page_setup['scale'] = round(595 / original_width, 4)
    
    rows = table.find_all('tr')
    
    target_cols = 6
    
    occupied = []
    
    processed_rows = []
    
    for row_idx, row in enumerate(rows):
        if row_idx == 0:
            date_text = ""
            title_text = ""
            cells = row.find_all(['td', 'th'])
            for cell in cells:
                text = cell.get_text(strip=True)
                if not text:
                    text = cell.get('x:str', '')
                if '2026年5月' in text:
                    date_text = text
                elif '义务教育学校教职工绩效工资审批表' in text:
                    title_text = text
            
            full_title = f"{date_text} {title_text}"
            processed_rows.append({
                'height': 27.0,
                'cells': [{
                    'text': full_title,
                    'rowspan': 1,
                    'colspan': target_cols,
                    'class': 'title',
                    'style': 'text-align:center;font-size:16pt;font-weight:bold;border:none;margin-bottom:10px;',
                    'no_border': True
                }]
            })
            occupied.append([None] * target_cols)
            continue
        
        if row_idx == 1:
            info_parts = []
            cells = row.find_all(['td', 'th'])
            for cell in cells:
                text = cell.get_text(strip=True)
                if not text:
                    text = cell.get('x:str', '')
                if text:
                    info_parts.append(text)
            
            full_info = ' '.join(info_parts)
            processed_rows.append({
                'height': 25.0,
                'cells': [{
                    'text': full_info,
                    'rowspan': 1,
                    'colspan': target_cols,
                    'class': 'info',
                    'style': 'text-align:left;font-size:11pt;border:none;padding-left:5px;margin-bottom:5px;',
                    'no_border': True
                }]
            })
            occupied.append([None] * target_cols)
            continue
        
        row_height = row.get('height', '50')
        height_match = re.search(r'([0-9.]+)', row_height)
        row_height_pt = float(height_match.group(1)) * 0.5 if height_match else 25
        
        cells = row.find_all(['td', 'th'])
        
        new_cells = []
        col_idx = 0
        
        cell_index = 0
        
        category_titles = ['行政管理人员', '专业技术人员', '工人', '绩效工资合计', '乡镇补贴合计', '岗位设置遗留问题', '退休干部', '退休工人', '离休干部']
        
        while col_idx < target_cols:
            if occupied[row_idx-2] and occupied[row_idx-2][col_idx]:
                col_idx += 1
                continue
            
            if cell_index >= len(cells):
                break
            
            cell = cells[cell_index]
            text = cell.get_text(strip=True)
            if not text:
                text = cell.get('x:str', '')
            
            rowspan = int(cell.get('rowspan')) if cell.get('rowspan') else 1
            colspan = int(cell.get('colspan')) if cell.get('colspan') else 1
            style = cell.get('style', '')
            class_name = cell.get('class', [''])[0] if cell.get('class') else ''
            
            if col_idx >= 4:
                if text and ('呈报单位意见' in text or '教育局意见' in text or '人事部门意见' in text):
                    colspan = 1
                elif text and ('同意呈报' in text or '盖章' in text or '根据相关文件' in text):
                    colspan = 1
                elif text == '' and colspan > 2:
                    colspan = 1
            
            if col_idx + colspan > target_cols:
                colspan = target_cols - col_idx
            
            is_category = col_idx == 0 and text in category_titles
            
            if is_category:
                colspan = 4
            
            new_cell = {
                'text': text,
                'rowspan': rowspan,
                'colspan': colspan,
                'class': class_name,
                'style': style,
                'no_border': 'border-right:none' in style or 'border-bottom:none' in style or 'border:none' in style,
                'align': 'left' if is_category else 'center'
            }
            new_cells.append(new_cell)
            
            if rowspan > 1:
                for r in range(1, rowspan):
                    next_row_idx = row_idx + r - 2
                    while len(occupied) <= next_row_idx:
                        occupied.append([None] * target_cols)
                    for c in range(colspan):
                        if col_idx + c < target_cols:
                            occupied[next_row_idx][col_idx + c] = True
            
            col_idx += colspan
            
            cell_index += 1
        
        while col_idx < target_cols:
            new_cells.append({
                'text': '',
                'rowspan': 1,
                'colspan': 1,
                'class': '',
                'style': '',
                'no_border': False,
                'align': 'center'
            })
            col_idx += 1
        
        all_empty = True
        for c in new_cells:
            if c['text']:
                all_empty = False
                break
        
        if not all_empty:
            processed_rows.append({
                'height': row_height_pt,
                'cells': new_cells
            })
            occupied.append([None] * target_cols)
    
    result = {
        'page_setup': page_setup,
        'col_widths': ['140', '75', '100', '85', '150', '257.75'],
        'rows': processed_rows,
        'total_rows': len(processed_rows),
        'total_cols': target_cols
    }
    
    output_dir = os.path.join(os.path.dirname(__file__), 'data')
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = os.path.join(output_dir, 'performance_pay_template.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"模板解析完成，保存到: {output_file}")
    print(f"总行数: {len(processed_rows)}")
    print(f"总列数: {target_cols}")
    
    return result

if __name__ == '__main__':
    parse_template()