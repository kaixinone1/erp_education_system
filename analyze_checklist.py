#!/usr/bin/env python3
"""分析清单模板配置"""
import psycopg2
import json

conn = psycopg2.connect(
    host="localhost",
    port="5432",
    database="taiping_education",
    user="taiping_user",
    password="taiping_password"
)
cursor = conn.cursor()

# 获取所有表名
cursor.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public'
""")
tables = [row[0] for row in cursor.fetchall()]
print("数据库中的表:", tables)

# 查找清单模板表
for table in tables:
    if 'checklist' in table.lower() or '清单' in table:
        print(f"\n找到清单表: {table}")
        cursor.execute(f"SELECT * FROM {table} LIMIT 1")
        cols = [desc[0] for desc in cursor.description]
        print(f"  字段: {cols}")

cursor.close()
conn.close()
