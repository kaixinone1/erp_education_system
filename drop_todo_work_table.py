import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port=5432,
    database='taiping_education',
    user='taiping_user',
    password='taiping_password'
)

cursor = conn.cursor()

print("=" * 80)
print("删除旧待办系统（todo_work 表）")
print("=" * 80)

# 删除表
cursor.execute("DROP TABLE IF EXISTS todo_work CASCADE")
conn.commit()

print("\n[OK] todo_work 表已删除")

# 验证
cursor.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema='public' AND table_name='todo_work'
""")
result = cursor.fetchone()

if result:
    print("[ERROR] 表仍然存在")
else:
    print("[OK] 确认表已删除")

cursor.close()
conn.close()
