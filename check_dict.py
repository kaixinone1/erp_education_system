"""
检查字典表中的任职状态数据
"""
import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port='5432',
    database='taiping_education',
    user='taiping_user',
    password='taiping_password'
)
cursor = conn.cursor()

# 查询字典表
cursor.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public' 
    AND table_name LIKE '%dict%'
    ORDER BY table_name
""")

print("字典表:")
for row in cursor.fetchall():
    print(f"  - {row[0]}")

# 查询 dict_dictionary 表
try:
    cursor.execute("""
        SELECT * FROM dict_dictionary LIMIT 10
    """)
    print("\ndict_dictionary 表数据:")
    columns = [desc[0] for desc in cursor.description]
    print(f"列名: {columns}")
    for row in cursor.fetchall():
        print(f"  {row}")
except Exception as e:
    print(f"查询失败: {e}")

# 查询是否有任职状态字典
try:
    cursor.execute("""
        SELECT table_name FROM information_schema.tables 
        WHERE table_name = 'dict_employment_status'
    """)
    if cursor.fetchone():
        print("\n找到 dict_employment_status 表")
        cursor.execute("SELECT * FROM dict_employment_status")
        for row in cursor.fetchall():
            print(f"  {row}")
    else:
        print("\n没有找到 dict_employment_status 表")
except Exception as e:
    print(f"查询失败: {e}")

cursor.close()
conn.close()
