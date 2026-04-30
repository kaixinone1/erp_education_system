from bs4 import BeautifulSoup

with open('templates/义务教育学校教职工绩效工资审批表html.html', 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')
table = soup.find('table')

# 分析表格结构
rows = table.find_all('tr')
print('总行数:', len(rows))

# 提取每个单元格的rowspan和colspan
print('\n表格结构分析:')
for i, row in enumerate(rows):
    cells = row.find_all(['td', 'th'])
    row_info = []
    for j, cell in enumerate(cells):
        text = cell.get_text(strip=True)[:15]
        rowspan = cell.get('rowspan', '1')
        colspan = cell.get('colspan', '1')
        row_info.append(f'{text}[r{rowspan}c{colspan}]')
    print(f'{i}: {" | ".join(row_info)}')
