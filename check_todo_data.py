#!/usr/bin/env python3
"""检查待办任务数据"""
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
print("待办任务数据检查")
print("=" * 80)

# 查询所有待办任务
cursor.execute("""
    SELECT id, 教师ID, 清单名称, 教师姓名, 状态, 总任务数, 已完成数, created_at
    FROM todo_work_items
    ORDER BY created_at DESC
""")

print("\n所有待办任务：")
print("-" * 80)
for row in cursor.fetchall():
    print(f"ID={row[0]}, 教师ID={row[1]}, 姓名={row[3]}, 状态={row[4]}, 总任务={row[5]}, 已完成={row[6]}")

# 统计
cursor.execute("SELECT 状态, COUNT(*) FROM todo_work_items GROUP BY 状态")
print("\n状态统计：")
for row in cursor.fetchall():
    print(f"  {row[0]}: {row[1]} 项")

cursor.close()
conn.close()

print("\n" + "=" * 80)
