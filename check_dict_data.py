#!/usr/bin/env python3
"""检查字典表数据"""
import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port=5432,
    database='taiping_education',
    user='taiping_user',
    password='taiping_password'
)
cursor = conn.cursor()

print("学历类型字典 (dict_education_type_dictionary):")
cursor.execute("SELECT * FROM dict_education_type_dictionary LIMIT 5")
for row in cursor.fetchall():
    print(f"  {row}")

print("\n学历层次字典 (dict_education_level_dictionary):")
cursor.execute("SELECT * FROM dict_education_level_dictionary LIMIT 5")
for row in cursor.fetchall():
    print(f"  {row}")

cursor.close()
conn.close()
