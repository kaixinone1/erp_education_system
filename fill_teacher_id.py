#!/usr/bin/env python3
"""为 teacher_education_record 表填充 teacher_id"""
import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port='5432',
    database='taiping_education',
    user='taiping_user',
    password='taiping_password'
)
cursor = conn.cursor()

# 根据 id_card 关联填充 teacher_id
cursor.execute("""
    UPDATE teacher_education_record ter
    SET teacher_id = tbi.id
    FROM teacher_basic_info tbi
    WHERE ter.id_card = tbi.id_card
    AND ter.teacher_id IS NULL
""")

updated_count = cursor.rowcount
print(f"已更新 {updated_count} 条记录的 teacher_id")

conn.commit()
cursor.close()
conn.close()
