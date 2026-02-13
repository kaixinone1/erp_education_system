#!/usr/bin/env python3
"""为 retirement_report_data 表添加个人身份字段"""
import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port='5432',
    database='taiping_education',
    user='taiping_user',
    password='taiping_password'
)
cursor = conn.cursor()

# 检查字段是否已存在
cursor.execute("""
    SELECT column_name 
    FROM information_schema.columns 
    WHERE table_name = 'retirement_report_data' AND column_name = '个人身份'
""")

if cursor.fetchone():
    print("个人身份字段已存在")
else:
    # 添加个人身份字段
    cursor.execute("""
        ALTER TABLE retirement_report_data 
        ADD COLUMN "个人身份" character varying(20)
    """)
    print("已添加个人身份字段")

conn.commit()
cursor.close()
conn.close()
