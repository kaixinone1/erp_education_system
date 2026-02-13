#!/usr/bin/env python3
"""清理数据库中的硬编码数据"""
import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port='5432',
    database='taiping_education',
    user='taiping_user',
    password='taiping_password'
)
cursor = conn.cursor()

# 检查 retirement_report_data 表中是否有硬编码的