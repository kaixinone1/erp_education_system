#!/usr/bin/env python3
import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port='5432',
    database='taiping_education',
    user='taiping_user',
    password='taiping_password'
)
cursor = conn.cursor()

# 检查模板ID
cursor.execute("SELECT id FROM document_templates WHERE template_id = %s", ('职工退休申报表html',))
template_row = cursor.fetchone()
template_id = template_row[0]

# 检查文化程序和文化程度的映射
print("检查文化相关字段映射:")
print("=" * 60)

for field_name in ['文化程序', '文化程度']:
    cursor.execute("""
        SELECT placeholder_name, intermediate_field 
        FROM template_field_mapping 
        WHERE template_id = %s AND placeholder_name = %s
    """, (template_id, field_name))
    
    row = cursor.fetchone()
    if row:
        print(f"  {{ {row[0]} }} -> {row[1]}")
    else:
        print(f"  {{ {field_name} }} -> 未映射")

# 检查数据库字段名
print("\n数据库字段:")
cursor.execute("""
    SELECT column_name 
    FROM information_schema.columns 
    WHERE table_name = 'retirement_report_data' 
    AND column_name LIKE '%文化%'
""")

for row in cursor.fetchall():
    print(f"  {row[0]}")

cursor.close()
conn.close()

print("\n" + "=" * 60)
print("问题: 模板中是'文化程序'，但数据库字段是'文化程度'")
