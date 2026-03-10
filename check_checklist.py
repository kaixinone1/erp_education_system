import psycopg2

conn = psycopg2.connect(host='localhost', port='5432', database='taiping_education', user='taiping_user', password='taiping_password')
cur = conn.cursor()

print("=== business_checklist 表结构 ===")
cur.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = 'business_checklist'
    ORDER BY ordinal_position
""")
for row in cur.fetchall():
    print(f"  {row[0]}: {row[1]}")

print("\n=== 清单模板数据 ===")
cur.execute('SELECT id, "清单名称", "关联模板ID" FROM business_checklist LIMIT 5')
for row in cur.fetchall():
    print(f"  ID:{row[0]}, 名称:{row[1]}, 关联模板ID:{row[2]}")

cur.close()
conn.close()
