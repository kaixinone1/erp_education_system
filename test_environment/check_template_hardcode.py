#!/usr/bin/env python3
"""检查模板文件中的硬编码内容"""
import re

template_path = r'd:\erp_thirteen\tp_education_system\backend\templates\职工退休申报表html.html'

with open(template_path, 'r', encoding='utf-8') as f:
    content = f.read()

print("=" * 70)
print("模板文件硬编码检查")
print("=" * 70)

# 查找所有中文字符
chinese_chars = re.findall(r'[\u4e00-\u9fa5]+', content)

# 过滤出可能是姓名的（2-4个字符）
possible_names = [c for c in chinese_chars if 2 <= len(c) <= 4]

# 统计出现次数
from collections import Counter
name_counts = Counter(possible_names)

print("\n出现次数较多的中文词（可能是硬编码姓名）:")
for name, count in name_counts.most_common(20):
    # 排除常见的非姓名词
    if name not in ['退休', '申报', '单位', '职务', '岗位', '薪级', '事业', '管理', '技术', '等级', '对应', '原职务', '工勤', '专技', '时间', '年月', '日期', '文化', '程度', '身份', '证号', '民族', '性别', '出生', '参加', '工作', '年限', '籍贯', '现住', '地址', '退休原因', '居住', '意见', '证明', '直系', '亲属', '供养', '情况', '备注', '独生子女', '入党', '技术职称', '工资', '襄阳', '太平', '枣阳', '湖北']:
        print(f"   {name}: {count} 次")

# 特别检查王德和王军峰
print("\n特别检查:")
if '王德' in content:
    print(f"   ✗ 发现硬编码'王德': {content.count('王德')} 次")
    # 显示位置
    idx = content.find('王德')
    print(f"   位置: {idx}")
else:
    print(f"   ✓ 未发现'王德'")

if '王军峰' in content:
    print(f"   ✗ 发现硬编码'王军峰': {content.count('王军峰')} 次")
else:
    print(f"   ✓ 未发现'王军峰'")

# 检查{{姓名}}
if '{{姓名}}' in content or '{{ 姓名 }}' in content:
    count1 = content.count('{{姓名}}')
    count2 = content.count('{{ 姓名 }}')
    print(f"\n   ✓ 发现{{{{姓名}}}}占位符: {count1 + count2} 次")
else:
    print(f"\n   ✗ 未找到{{{{姓名}}}}占位符")

print("\n" + "=" * 70)
