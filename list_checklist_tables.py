import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port='5432',
    database='taiping_education',
    user='taiping_user',
    password='taiping_password'
)
cursor = conn.cursor()

cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_name LIKE '%checklist%'")
rows = cursor.fetchall()

print('Checklist related tables:')
for row in rows:
    print(f'  - {row[0]}')

cursor.close()
conn.close()
