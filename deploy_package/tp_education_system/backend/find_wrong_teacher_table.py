#!/usr/bin/env python3
"""
查找119条记录的错误教师基础信息表
"""
import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port='5432',
    database='taiping_education',
    user='taiping_user',
    password='taiping_password'
)
cursor = conn.cursor()

# 查找所有表
print("=== 查找所有表 ===")
cursor.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public'
    ORDER BY table_name
""")

all_tables = cursor.fetchall()
for row in all_tables:
    table_name = row[0]
    # 获取记录数
    try:
        cursor.execute(f"SELECT COUNT(*) FROM \"{table_name}\"")
        count = cursor.fetchone()[0]
        if count == 119 or '教师' in table_name or 'teacher' in table_name.lower():
            print(f"  {table_name}: {count} 条记录")
    except:
        pass

# 特别检查可能的中文表名
print("\n=== 检查中文表名 ===")
cursor.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public'
    AND table_name LIKE '%教师%'
    ORDER BY table_name
""")
for row in cursor.fetchall():
    table_name = row[0]
    cursor.execute(f"SELECT COUNT(*) FROM \"{table_name}\"")
    count = cursor.fetchone()[0]
    print(f"  {table_name}: {count} 条记录")

# 检查所有有119条记录的表
print("\n=== 所有有119条记录的表 ===")
for row in all_tables:
    table_name = row[0]
    try:
        cursor.execute(f"SELECT COUNT(*) FROM \"{table_name}\"")
        count = cursor.fetchone()[0]
        if count == 119:
            # 检查表结构
            cursor.execute(f"""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = '{table_name}'
                ORDER BY ordinal_position
                LIMIT 5
            """)
            cols = cursor.fetchall()
            col_names = [c[0] for c in cols]
            print(f"  {table_name}: {count} 条记录, 字段: {col_names}")
    except:
        pass

cursor.close()
conn.close()
