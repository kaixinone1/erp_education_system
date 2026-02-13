#!/usr/bin/env python3
import psycopg2
import json
from datetime import datetime

conn = psycopg2.connect(
    host='localhost',
    port='5432',
    database='taiping_education',
    user='taiping_user',
    password='taiping_password'
)
cursor = conn.cursor()

template_id = '职工退休申报表html'

# 删除旧字段
cursor.execute("DELETE FROM template_field_mappings WHERE template_id = %s", (template_id,))
print(f'删除旧字段: {cursor.rowcount} 条')

# 添加296个字段
for i in range(296):
    cursor.execute("""
        INSERT INTO template_field_mappings 
        (template_id, field_name, field_label, field_type, position_type, position_data, default_value, data_source, sort_order, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        template_id,
        f'field_{i}',
        f'字段 {i+1}',
        'text',
        'coordinate',
        json.dumps({'index': i}),
        '',
        '',
        i,
        datetime.now()
    ))

print(f'添加新字段: 296 条')

conn.commit()
cursor.close()
conn.close()
print('完成！')
