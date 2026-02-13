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

# 查看document_templates表结构
cursor.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = 'document_templates'
    ORDER BY ordinal_position
""")

print("document_templates 表结构：")
for row in cursor.fetchall():
    print(f"  {row[0]}: {row[1]}")

# 查看是否有数据
cursor.execute("SELECT COUNT(*) FROM document_templates")
count = cursor.fetchone()[0]
print(f"\n表中数据条数: {count}")

if count > 0:
    cursor.execute("SELECT id, template_id, name, file_name FROM document_templates LIMIT 3")
    print("\n前3条数据：")
    for row in cursor.fetchall():
        print(f"  id={row[0]}, template_id={row[1]}, name={row[2]}, file_name={row[3]}")

cursor.close()
conn.close()
