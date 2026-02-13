#!/usr/bin/env python3
"""按指定格式打印占位符"""

categories = [
    ("基本信息", ["姓名", "性别", "出生日期", "民族", "籍贯", "现住址", "文化程度"]),
    ("工作信息", ["参加工作时间", "工作年限", "职务", "技术职称", "入党年月", "退休原因"]),
    ("家庭信息", ["是否独生子女", "直系亲属信息"]),
    ("工作经历", ["自何年何月", "至何年何月", "在何单位任何职", "证明人及其住址"]),
    ("岗位", [f"岗位{i}" for i in range(1, 10)]),
    ("职务", [f"职务{i}" for i in range(1, 7)]),
    ("技术等级", [f"技术等级{i}" for i in range(1, 4)]),
    ("薪级", [f"薪级{i}" for i in range(1, 10)]),
]

print("=" * 60)
print("职工退休申报表模板 - 占位符统计")
print("=" * 60)
print()

total = 0
for cat_name, fields in categories:
    count = len(fields)
    total += count
    print(f"{cat_name:12s}  {count:2d}个")

print("-" * 60)
print(f"{'合计':12s}  {total:2d}个")
print("=" * 60)
