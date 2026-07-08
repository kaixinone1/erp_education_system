import psycopg2

conn = psycopg2.connect(host='localhost', dbname='taiping_education', user='taiping_user', password='taiping_password')
cur = conn.cursor()

cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY table_name")
all_tables = [r[0] for r in cur.fetchall() if 'salary' in r[0].lower()]

print(f'All salary tables in database: {all_tables}')

for table in all_tables:
    cur.execute(f'SELECT COUNT(*) FROM {table}')
    count = cur.fetchone()[0]
    print(f'  {table}: {count} rows')

conn.close()