#!/usr/bin/env python3
"""检查 dict_education_level_dictionary 字典表"""
import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port='5432',
    database='taiping_education',
    user='taiping_user',
    password='taiping_password'
)
cursor = conn.cursor()

# 检查 dict_education_level_dictionary 表结构
cursor.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = 'dict_education_level_dictionary'
    ORDER BY ordinal_position
""")
print("dict_education_level_dictionary 表结构：")
for row in cursor.fetchall():
    print(f"  {row[0]}: {row[1]}")

# 检查数据
cursor.execute('SELECT * FROM dict_education_level_dictionary')
print("\ndict_education_level_dictionary 表内容：")
for row in cursor.fetchall():
    print(f"  {row}")

cursor.close()
conn.close()
