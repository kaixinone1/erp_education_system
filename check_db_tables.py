#!/usr/bin/env python3
"""
检查数据库中的实际表名
"""

import psycopg2

DB_PARAMS = {
    'host': 'localhost',
    'database': 'taiping_education',
    'user': 'taiping_user',
    'password': 'taiping_password'
}

conn = psycopg2.connect(**DB_PARAMS)
cursor = conn.cursor()

print("=" * 80)
print("数据库中的表")
print("=" * 80)

cursor.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public' 
    AND table_type = 'BASE TABLE'
    ORDER BY table_name
""")

tables = [row[0] for row in cursor.fetchall()]
for table in tables:
    print(f"  {table}")

print(f"\n总计: {len(tables)} 个表")

# 检查 table_name_mappings.json 中的映射
import json

with open(r'd:\erp_thirteen\tp_education_system\backend\config\table_name_mappings.json', 'r', encoding='utf-8') as f:
    mappings = json.load(f)

print("\n" + "=" * 80)
print("table_name_mappings.json 中的映射")
print("=" * 80)

print("\nmappings:")
for cn, info in mappings.get('mappings', {}).items():
    print(f"  {cn} -> {info.get('english_name')}")

print("\nreverse_mappings:")
for en, cn in mappings.get('reverse_mappings', {}).items():
    print(f"  {en} -> {cn}")

# 检查哪些表没有映射
print("\n" + "=" * 80)
print("没有中文映射的表")
print("=" * 80)

reverse = mappings.get('reverse_mappings', {})
for table in tables:
    if table not in reverse:
        print(f"  {table}")

cursor.close()
conn.close()
