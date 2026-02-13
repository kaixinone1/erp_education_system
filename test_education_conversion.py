#!/usr/bin/env python3
"""测试学历代码转换"""
import sys
import os

# 添加 backend 目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'tp_education_system', 'backend'))

from utils.dict_utils import get_education_name, get_dict_name

DATABASE_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "database": "taiping_education",
    "user": "taiping_user",
    "password": "taiping_password"
}

# 测试学历转换
print("测试学历代码转换:")
for code in [1, 2, 3, 4, 5, 6, 7, 8]:
    name = get_education_name(code, DATABASE_CONFIG)
    print(f"  {code} -> {name}")

print("\n测试完成!")
