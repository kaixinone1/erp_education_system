#!/usr/bin/env python3
"""
检查数据库中当前存在的表
"""

import psycopg2

DB_PARAMS = {
    'host': 'localhost',
    'database': 'taiping_education',
    'user': 'taiping_user',
    'password': 'taiping_password'
}

print("=" * 80)
print("数据库中当前存在的表")
print("=" * 80)

conn = psycopg2.connect(**DB_PARAMS)
cursor = conn.cursor()

cursor.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public' 
    AND table_type = 'BASE TABLE'
    ORDER BY table_name
""")

tables = [row[0] for row in cursor.fetchall()]

if tables:
    print(f"\n找到 {len(tables)} 个表:\n")
    for table in tables:
        print(f"  • {table}")
else:
    print("\n数据库中没有表")

print("\n" + "=" * 80)

# 特别检查测试表
test_tables = ['dict_talent_type', 'teacher_talent_type', 'teacher_basic']
print("\n检查特定测试表:")
for table in test_tables:
    cursor.execute("""
        SELECT EXISTS (
            SELECT 1 FROM information_schema.tables 
            WHERE table_name = %s AND table_schema = 'public'
        )
    """, (table,))
    exists = cursor.fetchone()[0]
    status = "✓ 存在" if exists else "✗ 不存在"
    print(f"  {status}: {table}")

cursor.close()
conn.close()

print("\n" + "=" * 80)
