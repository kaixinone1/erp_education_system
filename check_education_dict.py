#!/usr/bin/env python3
"""检查 dict_education_dictionary 字典表"""
import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port='5432',
    database='taiping_education',
    user='taiping_user',
    password='taiping_password'
)
cursor = conn.cursor()

# 检查 dict_education_dictionary 表
cursor.execute('SELECT * FROM dict_education_dictionary ORDER BY code')
print("dict_education_dictionary 表内容：")
for row in cursor.fetchall():
    print(f"  {row}")

cursor.close()
conn.close()
