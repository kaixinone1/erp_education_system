#!/usr/bin/env python3
"""测试数据聚合组件"""
import sys
import os

# 添加 backend 目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'tp_education_system', 'backend'))

from utils.data_aggregator import (
    DataAggregator, 
    PredefinedConfigs,
    aggregate_retirement_data,
    save_retirement_data
)

DATABASE_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "database": "taiping_education",
    "user": "taiping_user",
    "password": "taiping_password"
}

# 测试聚合 teacher_id=273 的数据
print("测试聚合 teacher_id=273 的退休呈报表数据:")
data = aggregate_retirement_data(273, DATABASE_CONFIG)

print("\n聚合结果:")
for key, value in data.items():
    print(f"  {key}: {value}")

# 保存到数据库
print("\n保存到数据库...")
success = save_retirement_data(273, DATABASE_CONFIG)
print(f"保存结果: {'成功' if success else '失败'}")

# 验证保存结果
import psycopg2
conn = psycopg2.connect(**DATABASE_CONFIG)
cursor = conn.cursor()
cursor.execute('SELECT "文化程度" FROM retirement_report_data WHERE teacher_id = 273')
row = cursor.fetchone()
print(f"\n验证 - 文化程度: {row[0] if row else 'NULL'}")
cursor.close()
conn.close()
