import psycopg2
import json

conn = psycopg2.connect(host='localhost', port='5432', database='taiping_education', user='taiping_user', password='taiping_password')
cur = conn.cursor()

# 注册到中间表
cur.execute("""
    INSERT INTO intermediate_tables (table_name, table_name_cn, description, is_active)
    VALUES ('retirement_certificate_data', '签发退休证数据', '记录退休证签发信息', true)
    ON CONFLICT (table_name) DO NOTHING
""")

conn.commit()
cur.close()
conn.close()
print("中间表注册完成")
