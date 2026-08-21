import psycopg2
conn = psycopg2.connect(host='localhost', port=5432, database='taiping_education', user='taiping_user', password='taiping_password')
c = conn.cursor()
c.execute('SELECT "模板id" FROM saved_exports WHERE id = 133')
r = c.fetchone()
print(f'模板ID: {r[0]}')
c.execute('SELECT "模板id", "模板名称" FROM template_configs')
for row in c.fetchall():
    print(f'  ID={row[0]}, name={row[1]}')
c.close()
conn.close()