#!/usr/bin/env python3
"""检查全系统字段来源"""
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
print("全系统字段来源分析")
print("=" * 80)

# 1. 检查所有表
cursor.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public' 
    AND table_type = 'BASE TABLE'
    ORDER BY table_name
""")

tables = cursor.fetchall()
print(f"\n【数据库共有 {len(tables)} 个表】")
for t in tables:
    print(f"   - {t[0]}")

# 2. 检查 retirement_report_data 表的字段
print("\n【retirement_report_data 表字段】")
cursor.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = 'retirement_report_data'
    ORDER BY ordinal_position
""")
for row in cursor.fetchall():
    print(f"   {row[0]} ({row[1]})")

# 3. 检查 teachers 表的字段
print("\n【teachers 表字段（部分）】")
cursor.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = 'teachers'
    ORDER BY ordinal_position
    LIMIT 15
""")
for row in cursor.fetchall():
    print(f"   {row[0]} ({row[1]})")

# 4. 检查 template_field_mapping 中的映射
print("\n【template_field_mapping 中的字段映射】")
cursor.execute("""
    SELECT tfm.placeholder_name, tfm.intermediate_field, dt.template_id
    FROM template_field_mapping tfm
    JOIN document_templates dt ON tfm.template_id = dt.id
    WHERE dt.template_id = '职工退休申报表html'
    ORDER BY tfm.placeholder_name
""")
for row in cursor.fetchall():
    print(f"   {{{{ {row[0]} }}}} -> {row[1]}")

cursor.close()
conn.close()

print("\n" + "=" * 80)
