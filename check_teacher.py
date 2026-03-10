import psycopg2

conn = psycopg2.connect(host='localhost', port='5432', database='taiping_education', user='taiping_user', password='taiping_password')
cur = conn.cursor()

# 检查教师ID=1是否存在
cur.execute("SELECT id, name FROM teacher_basic_info WHERE id = 1")
row = cur.fetchone()
if row:
    print(f"教师ID=1存在: {row}")
else:
    print("教师ID=1不存在")

# 列出前5个教师
print("\n前5个教师:")
cur.execute("SELECT id, name FROM teacher_basic_info LIMIT 5")
for row in cur.fetchall():
    print(f"  ID={row[0]}, 姓名={row[1]}")

cur.close()
conn.close()
