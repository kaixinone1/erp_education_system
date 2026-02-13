#!/usr/bin/env python3
"""
删除数据库中全部表结构和数据
"""

import psycopg2

DB_PARAMS = {
    'host': 'localhost',
    'database': 'taiping_education',
    'user': 'taiping_user',
    'password': 'taiping_password'
}

print("=" * 80)
print("删除数据库中全部表结构和数据")
print("=" * 80)

conn = psycopg2.connect(**DB_PARAMS)
cursor = conn.cursor()

# 获取所有表
cursor.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public' 
    AND table_type = 'BASE TABLE'
    ORDER BY table_name
""")

tables = [row[0] for row in cursor.fetchall()]
print(f"\n找到 {len(tables)} 个表，开始删除...")

# 删除所有表
for table in tables:
    try:
        cursor.execute(f'DROP TABLE IF EXISTS "{table}" CASCADE')
        print(f"  ✓ 已删除: {table}")
    except Exception as e:
        print(f"  ✗ 删除失败 {table}: {e}")

conn.commit()
cursor.close()
conn.close()

print("\n" + "=" * 80)
print(f"已删除全部 {len(tables)} 个表")
print("=" * 80)
