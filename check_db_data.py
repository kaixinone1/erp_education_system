"""
检查数据库中的实际数据
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

# 检查 teacher_id=293 的数据
cursor.execute("""
    SELECT 姓名, 性别, 个人编号, 薪级1, 事业管理岗位1
    FROM retirement_report_data 
    WHERE teacher_id = 293
""")

row = cursor.fetchone()
if row:
    print(f"teacher_id=293 的数据:")
    print(f"  姓名: {row[0]}")
    print(f"  性别: {row[1]}")
    print(f"  个人编号: {row[2]}")
    print(f"  薪级1: {row[3]}")
    print(f"  事业管理岗位1: {row[4]}")
else:
    print("没有找到 teacher_id=293 的数据")

# 检查所有数据
cursor.execute("SELECT teacher_id, 姓名 FROM retirement_report_data LIMIT 10")
rows = cursor.fetchall()
print(f"\n表中所有数据 (前10条):")
for r in rows:
    print(f"  teacher_id={r[0]}: 姓名={r[1]}")

cursor.close()
conn.close()
