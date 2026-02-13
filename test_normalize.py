#!/usr/bin/env python3
"""
测试数据类型标准化
"""

import sys
sys.path.append(r'd:\erp_thirteen\tp_education_system\backend')

from core.table_name_manager import TableNameManager

manager = TableNameManager()

# 测试标准化函数
test_types = [
    'VARCHAR',
    'CHARACTER VARYING',
    'character varying',
    'DATE',
    'INTEGER'
]

print("测试数据类型标准化:")
print("-" * 50)
for t in test_types:
    result = manager._normalize_data_type(t)
    print(f"  {t} -> {result}")

# 测试签名对比
print("\n测试签名对比:")
print("-" * 50)

# 模拟配置文件中的签名
saved_sig = [
    ('专业', 'STRING'),
    ('姓名', 'STRING'),
    ('身份证号码', 'STRING'),
]

# 模拟数据库中的签名
db_sig = [
    ('专业', 'CHARACTER VARYING'),
    ('姓名', 'CHARACTER VARYING'),
    ('身份证号码', 'CHARACTER VARYING'),
]

print(f"配置文件签名: {saved_sig}")
print(f"数据库签名: {db_sig}")

# 标准化数据库签名
normalized_db_sig = [(col, manager._normalize_data_type(dtype)) for col, dtype in db_sig]
print(f"标准化后签名: {normalized_db_sig}")

# 对比
result = manager._compare_signatures(saved_sig, normalized_db_sig)
print(f"\n对比结果: {result}")
