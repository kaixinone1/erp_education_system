import json

with open('data/performance_pay_template.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print('修改前列宽度:', data['col_widths'])

data['col_widths'] = ['84', '100', '100', '100', '75', 'auto']

print('修改后列宽度:', data['col_widths'])

with open('data/performance_pay_template.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print('JSON文件已更新')