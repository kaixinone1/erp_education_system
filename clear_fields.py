#!/usr/bin/env python3
import psycopg2
conn = psycopg2.connect(host='localhost', port='5432', database='taiping_education', user='taiping_user', password='taiping_password')
cursor = conn.cursor()

# 清空字段
cursor.execute("DELETE FROM template_field_mappings WHERE template_id = '职工退休申报表html'")
print(f'已删除 {cursor.rowcount} 个字段')

conn.commit()
cursor.close()
conn.close()
print('完成！')
