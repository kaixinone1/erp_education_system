#!/usr/bin/env python3
import psycopg2
conn = psycopg2.connect(host='localhost', port='5432', database='taiping_education', user='taiping_user', password='taiping_password')
cursor = conn.cursor()

# 查看字段数量
cursor.execute("SELECT COUNT(*) FROM template_field_mappings WHERE template_id = '职工退休申报表html'")
count = cursor.fetchone()[0]
print(f'字段数量: {count}')

# 查看前10个字段
cursor.execute("SELECT field_name, field_label FROM template_field_mappings WHERE template_id = '职工退休申报表html' ORDER BY sort_order LIMIT 10")
print('\n前10个字段:')
for row in cursor.fetchall():
    print(f'  {row[0]} - {row[1]}')

cursor.close()
conn.close()
