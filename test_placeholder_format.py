"""
测试占位符格式匹配
"""
# 模拟从文件提取的占位符（带花括号）
placeholders_from_file = ['{{姓名}}', '{{性别}}', '{{出生日期}}']

# 模拟从数据库读取的 mappings（纯字段名）
mappings = {
    '姓名': {'table': 'retirement_report_data', 'field': '姓名'},
    '性别': {'table': 'retirement_report_data', 'field': '性别'},
    '出生日期': {'table': 'retirement_report_data', 'field': '出生日期'},
}

print('测试占位符匹配:')
for placeholder in placeholders_from_file:
    field_name = placeholder.strip('{}')
    print(f'  占位符: {placeholder}')
    print(f'  处理后: {field_name}')
    print(f'  在mappings中: {field_name in mappings}')
    print()
