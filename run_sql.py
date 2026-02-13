#!/usr/bin/env python3
"""执行SQL创建新表"""
import psycopg2

conn = psycopg2.connect(
    host="localhost",
    port="5432",
    database="taiping_education",
    user="taiping_user",
    password="taiping_password"
)
cursor = conn.cursor()

# 读取并执行SQL
with open('d:/erp_thirteen/create_test_table.sql', 'r', encoding='utf-8') as f:
    sql = f.read()
    cursor.execute(sql)

conn.commit()

# 验证表是否创建成功
cursor.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = 'teacher_training_records' 
    ORDER BY ordinal_position
""")

print("✓ 新表 teacher_training_records 创建成功！")
print("\n表结构:")
for row in cursor.fetchall():
    print(f"  {row[0]}: {row[1]}")

# 查看数据
cursor.execute("SELECT * FROM teacher_training_records")
rows = cursor.fetchall()
print(f"\n✓ 已插入 {len(rows)} 条测试数据")

cursor.close()
conn.close()
print("\n现在可以直接访问: http://localhost:5173/auto-table/teacher_training_records")
