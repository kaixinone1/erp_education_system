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

# 先删除关联记录
cursor.execute("DELETE FROM template_usage_records WHERE template_id = '职工退休呈报表'")
print('删除使用记录:', cursor.rowcount, '条')

# 删除字段映射
cursor.execute("DELETE FROM template_field_mappings WHERE template_id = '职工退休呈报表'")
print('删除字段映射:', cursor.rowcount, '条')

# 再删除模板
cursor.execute("DELETE FROM document_templates WHERE template_id = '职工退休呈报表'")
print('删除模板:', cursor.rowcount, '条')

conn.commit()
cursor.close()
conn.close()
print('删除完成')
