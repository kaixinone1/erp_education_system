#!/usr/bin/env python3
"""检查退休呈报表的实际结构"""
import psycopg2

conn = psycopg2.connect(
    host="localhost",
    port="5432",
    database="taiping_education",
    user="taiping_user",
    password="taiping_password"
)
cursor = conn.cursor()

# 获取表结构
cursor.execute("""
    SELECT column_name, data_type, is_nullable
    FROM information_schema.columns
    WHERE table_name = 'retirement_report_data'
    ORDER BY ordinal_position
""")

print("retirement_report_data 表结构：")
for row in cursor.fetchall():
    print(f"  {row[0]}: {row[1]} (nullable: {row[2]})")

# 获取示例数据
cursor.execute("SELECT * FROM retirement_report_data LIMIT 1")
columns = [desc[0] for desc in cursor.description]
row = cursor.fetchone()

if row:
    print("\n示例数据：")
    for col, val in zip(columns, row):
        print(f"  {col}: {val}")

cursor.close()
conn.close()
