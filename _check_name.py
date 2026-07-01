import json, re

with open(r'd:\erp_thirteen\_test_preview.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

html = data.get('数据', {}).get('HTML', '')

# Check for any name in the HTML (names from the database: 张运勤, 贺其清, 赵明安, 杨献立, 邹言蕾)
for name in ['贺其清', '张运勤', '赵明安', '杨献立', '邹言蕾']:
    if name in html:
        print(f"Found name: {name}")
    else:
        print(f"Name NOT found: {name}")