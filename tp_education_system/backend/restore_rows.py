import json

with open('data/performance_pay_template.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

data['rows'][22]['cells'] = [
    {'text': '绩效工资合计', 'rowspan': 1, 'colspan': 1, 'class': '', 'style': '', 'no_border': False, 'align': 'center'},
    {'text': '357', 'rowspan': 1, 'colspan': 1, 'class': '', 'style': '', 'no_border': False, 'align': 'center'},
    {'text': '', 'rowspan': 1, 'colspan': 1, 'class': '', 'style': '', 'no_border': False, 'align': 'center'},
    {'text': '462311', 'rowspan': 1, 'colspan': 1, 'class': '', 'style': '', 'no_border': False, 'align': 'center'},
    {'text': '', 'rowspan': 1, 'colspan': 1, 'class': '', 'style': '', 'no_border': False, 'align': 'center'},
    {'text': '', 'rowspan': 1, 'colspan': 1, 'class': '', 'style': '', 'no_border': False, 'align': 'center'}
]

data['rows'][23]['cells'] = [
    {'text': '乡镇补贴合计', 'rowspan': 1, 'colspan': 1, 'class': '', 'style': '', 'no_border': False, 'align': 'center'},
    {'text': '356', 'rowspan': 1, 'colspan': 1, 'class': '', 'style': '', 'no_border': False, 'align': 'center'},
    {'text': '350', 'rowspan': 1, 'colspan': 1, 'class': '', 'style': '', 'no_border': False, 'align': 'center'},
    {'text': '124600', 'rowspan': 1, 'colspan': 1, 'class': '', 'style': '', 'no_border': False, 'align': 'center'},
    {'text': '', 'rowspan': 1, 'colspan': 1, 'class': '', 'style': '', 'no_border': False, 'align': 'center'},
    {'text': '', 'rowspan': 1, 'colspan': 1, 'class': '', 'style': '', 'no_border': False, 'align': 'center'}
]

data['rows'][24]['cells'] = [
    {'text': '岗位设置遗留问题', 'rowspan': 1, 'colspan': 1, 'class': '', 'style': '', 'no_border': False, 'align': 'center'},
    {'text': '李发金', 'rowspan': 1, 'colspan': 1, 'class': '', 'style': '', 'no_border': False, 'align': 'center'},
    {'text': '321.3', 'rowspan': 1, 'colspan': 1, 'class': '', 'style': '', 'no_border': False, 'align': 'center'},
    {'text': '321.3', 'rowspan': 1, 'colspan': 1, 'class': '', 'style': '', 'no_border': False, 'align': 'center'},
    {'text': '', 'rowspan': 1, 'colspan': 1, 'class': '', 'style': '', 'no_border': False, 'align': 'center'},
    {'text': '', 'rowspan': 1, 'colspan': 1, 'class': '', 'style': '', 'no_border': False, 'align': 'center'}
]

data['rows'][25]['cells'] = [
    {'text': '岗位设置遗留问题', 'rowspan': 1, 'colspan': 1, 'class': '', 'style': '', 'no_border': False, 'align': 'center'},
    {'text': '张照凯', 'rowspan': 1, 'colspan': 1, 'class': '', 'style': '', 'no_border': False, 'align': 'center'},
    {'text': '353.94', 'rowspan': 1, 'colspan': 1, 'class': '', 'style': '', 'no_border': False, 'align': 'center'},
    {'text': '353.94', 'rowspan': 1, 'colspan': 1, 'class': '', 'style': '', 'no_border': False, 'align': 'center'},
    {'text': '', 'rowspan': 1, 'colspan': 1, 'class': '', 'style': '', 'no_border': False, 'align': 'center'},
    {'text': '', 'rowspan': 1, 'colspan': 1, 'class': '', 'style': '', 'no_border': False, 'align': 'center'}
]

data['rows'][26]['cells'] = [
    {'text': '岗位设置遗留问题合计', 'rowspan': 1, 'colspan': 1, 'class': '', 'style': '', 'no_border': False, 'align': 'center'},
    {'text': '2', 'rowspan': 1, 'colspan': 1, 'class': '', 'style': '', 'no_border': False, 'align': 'center'},
    {'text': '', 'rowspan': 1, 'colspan': 1, 'class': '', 'style': '', 'no_border': False, 'align': 'center'},
    {'text': '675.24', 'rowspan': 1, 'colspan': 1, 'class': '', 'style': '', 'no_border': False, 'align': 'center'},
    {'text': '', 'rowspan': 1, 'colspan': 1, 'class': '', 'style': '', 'no_border': False, 'align': 'center'},
    {'text': '', 'rowspan': 1, 'colspan': 1, 'class': '', 'style': '', 'no_border': False, 'align': 'center'}
]

data['rows'][27]['cells'] = [
    {'text': '退休干部', 'rowspan': 1, 'colspan': 1, 'class': '', 'style': '', 'no_border': False, 'align': 'center'},
    {'text': '447', 'rowspan': 1, 'colspan': 1, 'class': '', 'style': '', 'no_border': False, 'align': 'center'},
    {'text': '', 'rowspan': 1, 'colspan': 1, 'class': '', 'style': '', 'no_border': False, 'align': 'center'},
    {'text': '', 'rowspan': 1, 'colspan': 1, 'class': '', 'style': '', 'no_border': False, 'align': 'center'},
    {'text': '', 'rowspan': 1, 'colspan': 1, 'class': '', 'style': '', 'no_border': False, 'align': 'center'},
    {'text': '', 'rowspan': 1, 'colspan': 1, 'class': '', 'style': '', 'no_border': False, 'align': 'center'}
]

data['rows'][28]['cells'] = [
    {'text': '退休工人', 'rowspan': 1, 'colspan': 1, 'class': '', 'style': '', 'no_border': False, 'align': 'center'},
    {'text': '2', 'rowspan': 1, 'colspan': 1, 'class': '', 'style': '', 'no_border': False, 'align': 'center'},
    {'text': '', 'rowspan': 1, 'colspan': 1, 'class': '', 'style': '', 'no_border': False, 'align': 'center'},
    {'text': '', 'rowspan': 1, 'colspan': 1, 'class': '', 'style': '', 'no_border': False, 'align': 'center'},
    {'text': '', 'rowspan': 1, 'colspan': 1, 'class': '', 'style': '', 'no_border': False, 'align': 'center'},
    {'text': '', 'rowspan': 1, 'colspan': 1, 'class': '', 'style': '', 'no_border': False, 'align': 'center'}
]

data['rows'][29]['cells'] = [
    {'text': '离休干部', 'rowspan': 1, 'colspan': 1, 'class': '', 'style': '', 'no_border': False, 'align': 'center'},
    {'text': '1', 'rowspan': 1, 'colspan': 1, 'class': '', 'style': '', 'no_border': False, 'align': 'center'},
    {'text': '', 'rowspan': 1, 'colspan': 1, 'class': '', 'style': '', 'no_border': False, 'align': 'center'},
    {'text': '', 'rowspan': 1, 'colspan': 1, 'class': '', 'style': '', 'no_border': False, 'align': 'center'},
    {'text': '', 'rowspan': 1, 'colspan': 1, 'class': '', 'style': '', 'no_border': False, 'align': 'center'},
    {'text': '', 'rowspan': 1, 'colspan': 1, 'class': '', 'style': '', 'no_border': False, 'align': 'center'}
]

with open('data/performance_pay_template.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print('已恢复以下行的原始样式：')
print('  - 绩效工资合计')
print('  - 乡镇补贴合计')
print('  - 岗位设置遗留问题')
print('  - 岗位设置遗留问题')
print('  - 岗位设置遗留问题合计')
print('  - 退休干部')
print('  - 退休工人')
print('  - 离休干部')