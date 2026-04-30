import psycopg2
import json
conn = psycopg2.connect(host='localhost', port='5432', database='taiping_education', user='taiping_user', password='taiping_password')
cur = conn.cursor()
cur.execute('SELECT id, "清单名称" FROM business_checklist')
print('=== business_checklist ===')
for row in cur.fetchall():
    print(f'ID:{row[0]} 名称:{row[1]}')
conn.close()
