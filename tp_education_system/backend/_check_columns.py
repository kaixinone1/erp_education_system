import psycopg2
conn = psycopg2.connect(host='localhost', database='taiping_education', user='taiping_user', password='taiping_password')
cursor = conn.cursor()

# Get some sample tables and their column names
cursor.execute("""
    SELECT table_name, column_name 
    FROM information_schema.columns 
    WHERE table_schema = 'public' 
    AND table_name NOT LIKE 'pg_%' 
    AND table_name NOT LIKE 'sql_%'
    ORDER BY table_name, ordinal_position
    LIMIT 50
""")
for r in cursor.fetchall():
    print(f'{r[0]}: {r[1]}')

cursor.close()
conn.close()