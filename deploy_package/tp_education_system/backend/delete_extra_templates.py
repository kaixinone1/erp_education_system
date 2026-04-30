import psycopg2
conn = psycopg2.connect(host='localhost', port='5432', database='taiping_education', user='taiping_user', password='taiping_password')
cur = conn.cursor()

# 删除用户没有设计的多余模板
cur.execute("DELETE FROM todo_templates WHERE template_code IN ('RETIREMENT_APPROVAL', 'OCTOGENARIAN_SUBSIDY', 'MIGRATED_6', 'MIGRATED_5', 'MIGRATE_3', 'MIGRATED_4')")
deleted = cur.rowcount

conn.commit()
print(f'已删除 {deleted} 个多余模板')

conn.close()
