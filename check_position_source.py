#!/usr/bin/env python3
"""检查岗位字段的实际数据来源"""
import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port='5432',
    database='taiping_education',
    user='taiping_user',
    password='taiping_password'
)
cursor = conn.cursor()

print("=" * 80)
print("检查岗位字段数据来源")
print("=" * 80)

# 1. 检查 retirement_report_data 表中的岗位字段
print("\n【1. retirement_report_data 表中的岗位数据】")
cursor.execute("SELECT teacher_id, 岗位 FROM retirement_report_data WHERE 岗位 IS NOT NULL LIMIT 5")
rows = cursor.fetchall()
if rows:
    for row in rows:
        print(f"   teacher_id={row[0]}, 岗位={row[1]}")
else:
    print("   没有数据")

# 2. 检查所有表中有岗位字段的表
print("\n【2. 包含岗位字段的表】")
cursor.execute("""
    SELECT table_name, column_name 
    FROM information_schema.columns 
    WHERE column_name LIKE '%岗位%' 
    ORDER BY table_name
""")
for row in cursor.fetchall():
    print(f"   {row[0]}.{row[1]}")

# 3. 检查 teacher_basic_info 表
print("\n【3. teacher_basic_info 表中的岗位数据】")
try:
    cursor.execute("SELECT id, 岗位 FROM teacher_basic_info WHERE 岗位 IS NOT NULL LIMIT 5")
    rows = cursor.fetchall()
    if rows:
        for row in rows:
            print(f"   id={row[0]}, 岗位={row[1]}")
    else:
        print("   没有数据")
except Exception as e:
    print(f"   错误: {e}")

# 4. 检查 teachers 表
print("\n【4. teachers 表结构】")
cursor.execute("""
    SELECT column_name 
    FROM information_schema.columns 
    WHERE table_name = 'teachers'
""")
columns = [row[0] for row in cursor.fetchall()]
print(f"   字段: {', '.join(columns)}")

cursor.close()
conn.close()

print("\n" + "=" * 80)
