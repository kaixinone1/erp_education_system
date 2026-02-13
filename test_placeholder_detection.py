#!/usr/bin/env python3
import re

# 模拟模板内容
test_content = """
<html>
<head>
<style>
.xl91 {mso-style-parent:style0; text-align:center;}
</style>
</head>
<body>
<table>
<tr><td>{姓名}</td><td>{性别}</td></tr>
<tr><td>{身份证号}</td><td>{出生日期}</td></tr>
<tr><td>{民族}</td><td>{籍贯}</td></tr>
</table>
<input type="text" value="{职务}" />
</body>
</html>
"""

# 方法1: 查找HTML标签中的占位符
pattern1 = r'>([^<]*\{[^{}]+\}[^<]*)<'
matches1 = re.findall(pattern1, test_content)
print("方法1 - HTML标签中的占位符:")
for m in matches1:
    inner = re.findall(r'\{([^{}]+)\}', m)
    print(f"  找到: {inner}")

# 方法2: input标签
pattern2 = r'<input[^>]*(?:value|placeholder)=["\']?\{([^{}]+)\}["\']?[^>]*>'
matches2 = re.findall(pattern2, test_content, re.IGNORECASE)
print("\n方法2 - input标签中的占位符:")
for m in matches2:
    print(f"  找到: {m}")

# 方法3: 过滤CSS
pattern3 = r'\{([^{}]+)\}'
all_matches = re.findall(pattern3, test_content)
valid = []
for match in all_matches:
    if any(kw in match for kw in ['mso-', 'style', 'font', 'border']):
        continue
    if match.isdigit():
        continue
    if ':' in match or ';' in match:
        continue
    if re.match(r'^[\u4e00-\u9fa5a-zA-Z0-9_]+$', match.strip()):
        valid.append(match.strip())

print("\n方法3 - 过滤后的有效占位符:")
for m in set(valid):
    print(f"  找到: {m}")
